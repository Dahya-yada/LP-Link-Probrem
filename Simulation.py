# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326

import copy
import numpy

import Network
import Data
import LpModel

class Simulation(object):
    """
    シミュレーションを実行する．
    """
    def __init__(self, data, model):
        self.DATA  = data
        self.MODEL = model
    
    def solve(self):
        for s in self.DATA.graph.site_list:
            self.MODEL.model(s)
            self.MODEL.MODEL.optimize()

            for d in self.DATA.graph.site_list:
                for ln in self.DATA.graph.both_link_list:
                    if (ln[0], ln[1]) in self.DATA.sites_x_tmp[s]:
                        self.DATA.sites_x_tmp[s][ln[0], ln[1]] += self.MODEL.X[d, ln[0], ln[1]].x * self.DATA.signal_now
                    if (ln[1], ln[0]) in self.DATA.sites_x_tmp[s]:
                        self.DATA.sites_x_tmp[s][ln[1], ln[0]] += self.MODEL.X[d, ln[0], ln[1]].x * self.DATA.signal_now
    
        min_dev_site = self.calc_std_dev()
        self.DATA.sites_x_sig[s] = copy.deepcopy(self.DATA.sites_x_tmp[s])
        self.DATA.sites_x_tmp    = self.make_site_link_dict() 

        self.DATA.vm_num[min_dev_site] += 1

    def calc_std_dev(self):
        std_dev_tmp = {k: 0 for k in self.DATA.graph.site_list}

        for s in self.DATA.graph.site_list:
            std_dev_tmp[s] = numpy.std(self.DATA.sites_x_tmp[s].values())
    
        min_dev_site = std_dev_tmp.items(), key=lambda x:x[1])[0]
        self.DATA.std_dev[self.DATA.try_now] = std_dev_tmp[min_dev_site]

        return min_dev_site

    








# MAIN
if __name__ == '__main__':
    node     = 100
    site     = 10
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 200

    graph = Network.Topology(node, site, connects=3)
    data  = Data.Data(graph, link_max, sig_max, sig_div, vm_add)
    model = LpModel.Model(data)
    simu  = Simulation(data,model)
    simu.solve()

