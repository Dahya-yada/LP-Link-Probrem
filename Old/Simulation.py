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

        self.x_sig        = {s: {l: 0 for l in o_graph.link_list} for s in o_graph.site_list}
        self.x_sig_solve  = {s: {l: 0 for l in o_graph.link_list} for s in o_graph.site_list}
        self.x_sig_result = {s: {l: 0 for l in o_graph.link_list} for s in o_graph.site_list}
        self.x_sig_matrix = {(i, j): 0 for i in range(o_graph.node_num) for j in range(o_graph.node_num)}

        self.sig_lb_tmp = self.Data.signal_lb
        self.add_site   = -1


    def solve(self):
        """
        1回だけすべての拠点に対し，線形計画法を解く
        """
        self.change_sig_bandwidth()
        self.make_x_sig_solve()
        print "[solve]",
        for s in self.Graph.site_list:
            print "*{}:".format(s)
            self.change_signal_vm(s)
            self.make_x_sig_matrix(s)
            self.Model.make_model(s, self.x_sig_matrix)
            self.Model.MODEL.optimize()
            self.update_result_x(s)
        self.decide_site()
        self.update_x_sig(self.add_site)
        self.update_data_x_sig()
    
    def change_sig_bandwidth(self):
        """
        LBへの信号量が増減した場合，割当済みリンク帯域を変更する．
        """
        if self.Data.signal_lb > self.sig_lb_tmp:
            inc = self.Data.signal_lb / self.sig_lb_tmp

            tmp = {s: {l: self.x_sig[s][l] * inc for l in self.Graph.link_list} for s in self.Graph.site_list}
            self.x_sig = copy.deepcopy(tmp)

    def change_signal_vm(self, s):
        """
        新しいVMが担当する信号量を変更する．
        """
        sig = self.Data.signal_lb / self.Graph.site_num / (self.Data.vm_num[s] + 1.0)
        self.Data.signal_vm = sig

    def make_x_sig_solve(self):
        """
        線形計画法を解くためのx_sig_solveを生成する．
        """
        tmp = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}
        for s in self.Graph.site_list:
            inc = (self.Data.vm_num[s] *1.00) / (self.Data.vm_num[s] + 1)
            v   = 0 
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
        w = 1
        if s == self.add_site:
            w = 10
        n = range(self.Graph.node_num)
        tmp = {(i, j): self.Data.bandwidth_max for i in n for j in n}

        for l in self.Graph.link_list:
            tmp[l[0], l[1]] = int(self.x_sig_solve[s][l[0], l[1]]) 
            tmp[l[1], l[0]] = int(self.x_sig_solve[s][l[0], l[1]]) 
        self.x_sig_matrix = copy.deepcopy(tmp)
        # for ll in self.Graph.both_link_list:
        #     print ll, self.x_sig_matrix[ll],
        # print ""
    
    def update_result_x(self, s):
        """
        最適化結果をx_sig_solveとx_sig_resultに反映します．
        """

        for l in self.Graph.link_list:
            for d in self.Graph.site_list:
                self.x_sig_solve[s][l]  += self.Model.X[d, l[0], l[1]].x * self.Data.signal_vm
                self.x_sig_solve[s][l]  += self.Model.X[d, l[1], l[0]].x * self.Data.signal_vm
                self.x_sig_result[s][l] += self.Model.X[d, l[0], l[1]].x * self.Data.signal_vm
                self.x_sig_result[s][l] += self.Model.X[d, l[1], l[0]].x * self.Data.signal_vm
    
    def decide_site(self):
        """
        最適化結果からVMを追加する拠点を決定する．
        """
        std_dev = {s: numpy.std(self.x_sig_solve[s].values()) for s in self.Graph.site_list}
        d_site  = min(std_dev.items(), key=lambda x: x[1])[0]
        self.Data.std_dev[self.Data.try_now] = std_dev[d_site]
        self.Data.vm_num[d_site] += 1
        self.add_site = d_site
        print "\n[add site]", d_site, "[std_dev]", std_dev[d_site]
    
    def update_x_sig(self, s):
        """
        決定した拠点からの仮想リンク帯域をx_sigに反映する．
        """
        inc = (self.Data.vm_num[s] - 1.0) / self.Data.vm_num[s]
        for l in self.Graph.link_list:
            self.x_sig[s][l] = int(self.x_sig[s][l] * inc)
            self.x_sig[s][l] = int(self.x_sig[s][l] + self.x_sig_result[s][l])
        self.x_sig_result = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}

    def update_data_x_sig(self):
        """
        Data.x_sigを更新する．
        """
        tmp = {l: 0 for l in self.Graph.link_list}
        
        for s in self.Graph.site_list:
            for l in self.Graph.link_list:
                tmp[l] += self.x_sig[s][l]
        
        self.Data.x_sig = copy.deepcopy(tmp)
        print self.Data.x_sig
        print ""








            





if __name__ == '__main__':
    import Network
    import Data
    import Model

    node     = 30
    site     = 5
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 20

    graph  = Network.Topology(node, site, connects=3)
    data   = Data.Data(graph, link_max, sig_max, sig_div, vm_add)
    model  = Model.Model(data)
    sim    = Simulation(graph, data, model)
    
    while data.try_now < data.try_num:
        print "--- {} ---".format(data.try_now + 1)
        sim.solve()
        data.try_now += 1