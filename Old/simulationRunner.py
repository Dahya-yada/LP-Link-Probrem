# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable=C0326

import Simulation as Simu
import Network
import Data
import Model

class Runner(object):
    """
    シミュレーションを実行し，データを生成するクラス．
    """
    def __init__(self, o_data, o_model):
        self.DATA  = o_data
        self.MODEL = o_model
        self.SIMU  = Simu.Simulation(o_data.graph, o_data, o_model)

    def run(self):
        while self.DATA.try_now < self.DATA.try_num:
            print "--- {} ---".format(self.DATA.try_now + 1)
            self.SIMU.solve()
            #print self.DATA.x_sig
            self.DATA.try_now += 1

        for idx in self.DATA.std_dev:
            print "{}, {}".format(idx, self.DATA.std_dev[idx])


if __name__ == '__main__':
    # node     = 100
    # site     = 10
    # connect  = 3
    # link_max = 20 * 1024 * 1024
    # sig_max  = 4 * 20000
    # sig_div  = 20
    # vm_add   = 2
    
    node     = 30
    site     = 5
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 20

    graph  = Network.Topology(node, site, connects=3)
    print "link_num:", len(graph.link_list)
    data   = Data.Data(graph, link_max, sig_max, sig_div, vm_add)
    model  = Model.Model(data)
    runner = Runner(data,model)
    runner.run()
