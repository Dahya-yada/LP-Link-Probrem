# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable=C0326

import copy
import numpy

class Simulation(object):
    """
    シミュレーションを実行する．
    """

    def __init__(self, o_graph, o_data, o_model):
        self.Graph = o_graph
        self.Data  = o_data
        self.Model = o_model

        self.x_sig        = {s: {l: 0 for l in o_graph.link_list} for o_graph.site_list}
        self.x_sig_solve  = {s: {l: 0 for l in o_graph.link_list} for o_graph.site_list}
        self.x_sig_result = {s: {l: 0 for l in o_graph.link_list} for o_graph.site_list}
        self.x_sig_matrix = {(i, j): 0 for i in range(o_graph.node_num) for j in range(o_graph.node_num)}

        self.sig_lb_tmp = self.Data.signal_lb


    def solve(self):
        """
        1回だけすべての拠点に対し，線形計画法を解く
        """
        pass
    
    def change_sig_bandwidth(self):
        """
        LBへの信号量が増減した場合，割当済みリンク帯域を変更する．
        """
        if self.Data.signal_lb > self.sig_lb_tmp:
            inc = self.Data.signal_lb / self.sig_lb_tmp

            tmp = {s: {l: self.x_sig[s][l] * inc for l in self.Graph.link_list} for s in self.Graph.site_list}
            self.x_sig = copy.deepcopy(tmp)

    def make_x_sig_solve(self):
        """
        線形計画法を解くためのx_sig_solveを生成する．
        """
        for s in self.Graph.site_list:
            inc = self.Data.vm_num[s] / (self.Data.vm_num[s] + 1)
            
            tmp = {s: {l: 0 for l in o_graph.link_list} for o_graph.site_list}
            v   = 0 
            for s in self.Graph.site_list:
                for l in self.Graph.link_list:
                    v = 0
                    for ss in self.Graph.site_list:
                        if s == ss:
                            v += self.x_sig[ss][l] * inc
                        else:
                            v += self.x_sig[ss][l]
                    tmp[s][l] = v
        self.x_sig_solve = copy.deepcopy(tmp)
    
    def make_x_sig_matrix(self, s):
        """
        線形計画法を解くために必要なx_sig_matrixを生成する．
        """
        n = range(self.Graph.node_num)
        tmp = {(i, j): self.Data.bandwidth_max for i in  for n for j in n}

        for l in self.Graph.link_list:
            tmp[l[0], l[1]] = self.x_sig_solve[s][l[0], l[1]]
            tmp[l[1], l[0]] = self.x_sig_solve[s][l[1], l[0]]


            





if __name__ == '__main__':
    import Network
    import Data
    import Model

    node     = 100
    site     = 10
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 20

    graph  = Network.Topology(node, site, connects=3)
    data   = Data.Data(graph, link_max, sig_max, sig_div, vm_add)
    model  = Model.Model(data)
    sim    = Simulation(graph, data, model)