# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import numpy

class Simulator(object):
    """
    シミュレーションを実行する．
    """

    def __init__(self, o_graph, o_model, bandwidth_max, link_num_max, signal_traffic_max, signal_division, vm_add_num):
        self.Graph       = o_graph
        self.Model       = o_model
        self.sig_trf_max = signal_traffic_max
        self.sig_div     = signal_division
        self.link_max    = bandwidth_max
        self.link_num    = link_num_max
        self.trial_num   = vm_add_num

        self.x_sig       = {l: 0 for l in self.Graph.link_list}
        self.x_sig_trf   = {s: 0 for s in self.Graph.site_list}
        self.x_sig_m     = {s: 0 for s in self.Graph.site_list}
        self.vm_num      = {s: 0 for s in self.Graph.site_list}
        self.x_sig_num   = {l: 0 for l in self.Graph.link_list}
        self.x_sig_num_s = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}
        self.x_sig_solve = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}
    
    def solve(self):
        """
        1回だけ線形計画法を解く
        """
        for s in self.Graph.site_list:
            matrix = self.make_link_num_matrix()
            self.Model.optimize(s, self.link_num, matrix, 'y')
            self.make_x_sig_solve(s)
            self.x_sig_m[s] = int(self.Model.M.x)

    def make_link_num_matrix(self):
        """
        線形計画法に使う，[i,j] = 割当リンク数 のマトリックスを生成する．
        """
        n   = self.Graph.node_num
        tmp = {(i,j): self.link_num for i in range(n) for j in range(n)}

        for l   in self.Graph.both_link_list:
            tmp[l] = 0
        for i,j in self.Graph.link_list:
            tmp[i, j] = int(self.x_sig_num[i, j])
            tmp[j, i] = int(self.x_sig_num[i, j])
        return tmp

    def make_x_sig_solve(self, s):
        """
        最適化結果をx_sig_solve[s]に保存する．
        """
        tmp = {(i,j): 0 for i,j in self.Graph.link_list}
        for d in self.Model.route:
            for i,j in tmp:
                if (i,j) in self.Model.route[d]:
                    tmp[i,j] += 1
                if (j,i) in self.Model.route[d]:
                    tmp[i,j] += 1
        self.x_sig_solve[s] = copy.deepcopy(tmp)






if __name__ == '__main__':
    import Network
    import Model

    node         = 30
    site         = 3
    connect      = 5
    link_num_max = 100
    link_max     = 20 * 1024 * 1024
    sig_max      = 4 * 20000
    sig_div      = 20
    vm_add       = 20

    graph = Network.Topology(node, site, connects=3)
    model = Model.Model(graph)
    simu  = Simulator(graph, model, link_max, link_num_max, sig_max, sig_div, vm_add)
    simu.solve()
