# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326

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
        for site in self.DATA.graph.site_list:
            self.MODEL.model(site)
            self.MODEL.MODEL.optimize()

            for d in self.DATA.graph.site_list:
                for link in self.DATA.graph.both_link_list:
                    if self.MODEL.X[d,link[0], link[1]].x > 0:
                        print site, d, link[0], link[1]







# MAIN
if __name__ == '__main__':
    node     = 100
    site     = 10
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20

    graph = Network.Topology(node, site, connects=3)
    data  = Data.Data(graph, link_max, sig_max, sig_div)
    model = LpModel.Model(data)
    simu  = Simulation(data,model)
    simu.solve()

