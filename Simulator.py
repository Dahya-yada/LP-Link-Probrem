# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import numpy

class Simulator(object):
    """
    シミュレータ本体
    """
    def __init__(self, o_graph, o_model, bandwidth_max, signal_traffic_max, signal_division, vm_add_num):
        self.Graph     = o_graph
        self.Model     = o_model
        self.link_max  = bandwidth_max
        self.t_sig_max = signal_traffic_max
        self.t_sig_div = signal_division
        self.t_sig_lb  = signal_traffic_max / signal_division
        self.t_sig_tmp = signal_traffic_max / signal_division
        self.try_num   = vm_add_num
        self.try_now   = 0
        self.vm_num    = {s: 0 for s in self.Graph.site_list}
        self.std_dev   = {n: 0 for n in range(vm_add_num)}

        self.x_sig           = {l: 0 for l in self.Graph.link_list}
        self.x_sig_s         = {s: {l :0 for l in self.Graph.link_list} for s in self.Graph.site_list}
        self.x_sig_solve     = {s: {l :0 for l in self.Graph.link_list} for s in self.Graph.site_list}
        self.x_sig_matrix    = {}
        self.x_sig_allocated = {s: {l :0 for l in self.Graph.link_list} for s in self.Graph.site_list}

        self.v_M = {}

    def solve(self):
        """
        1回だけ線形計画法による最適化を行う．
        """
        self.change_allocated_link()
        self.v_M = {}
        for s in self.Graph.site_list:
            self.make_sig_solve(s)
            self.make_x_sig_matrix(s)
            self.Model.make_model(s, self.link_max, self.x_sig_matrix, self.make_sig_vm(s))
            self.Model.optimize(s, "yes")
            self.v_M[s] = int(self.Model.M.x)
            self.make_x_sig_allocated(s)
            self.update_x_sig_solve(s)
        d_site = self.decide_add_site()
        print "[ADD SITE]", d_site
        self.update_x_sig_s(d_site)
        self.vm_num[d_site] += 1
        self.update_x_sig(s)
        #print self.x_sig
        print ""


    def change_allocated_link(self):
        """
        信号量に応じて割当済み仮想リンク帯域を変更する．
        """
        weight = 1.0 * self.t_sig_lb / self.t_sig_tmp
        if weight != 1:
            tmp = {s: {l: self.x_sig_s[s][l] * weight for l in self.Graph.link_list} for s in self.Graph.site_list}
            self.x_sig_s = copy.deepcopy(tmp)
    
    def make_sig_solve(self, s):
        """
        sig_solve[s]を生成する．
        """
        tmp    = {l :0 for l in self.Graph.link_list}
        weight = self.vm_num[s] / (self.vm_num[s] + 1)

        for ss in self.Graph.site_list:
            for l in self.Graph.link_list:
                if ss == s:
                    tmp[l] += self.x_sig_s[ss][l] * weight
                else:
                    tmp[l] += self.x_sig_s[ss][l]
        self.x_sig_solve[s] = copy.deepcopy(tmp)

    def make_sig_vm(self, s):
        """
        新しいVMが担当する信号量（線形計画法計算用）
        """
        return self.t_sig_lb / self.Graph.site_num

    def make_x_sig_matrix(self, s):
        """
        x_sig_matrixを生成する．
        """
        n   = self.Graph.node_num
        tmp = {(i, j): self.link_max for i in range(n) for j in range(n)}
        for l in self.Graph.link_list:
            tmp[l[0], l[1]] = self.x_sig_solve[s][l[0], l[1]]
            tmp[l[1], l[0]] = self.x_sig_solve[s][l[0], l[1]]
        self.x_sig_matrix = copy.deepcopy(tmp)

    def make_x_sig_allocated(self, s):
        """
        x_sig_allocatedを作成する．
        """
        tmp = {l: 0 for l in self.Graph.link_list}
        trf = 1.0 * self.t_sig_lb / self.Graph.site_num / (self.vm_num[s] + 1)
        for d in self.Graph.site_list:
            for l in self.Model.non_loop_route[d]:
                if (l[0], l[1]) in tmp:
                    tmp[l[0], l[1]] += trf
                if (l[1], l[0]) in tmp:
                    tmp[l[1], l[0]] += trf
        self.x_sig_allocated[s] = copy.deepcopy(tmp)
    
    def update_x_sig_solve(self, s):
        """
        x_sig_solveを更新する．
        """
        for l in self.Graph.link_list:
            self.x_sig_solve[s][l] += self.x_sig_allocated[s][l]
    
    def decide_add_site(self):
        """
        VMを追加する拠点を決定する．
        """
        d_site = min(self.v_M.items(), key=lambda x: x[1])[0]
        std_dev = {s: numpy.std(self.x_sig_solve[s].values()) for s in self.Graph.site_list}
        # d_site  = min(std_dev.items(), key=lambda x: x[1])[0]
        self.std_dev[self.try_now] = std_dev[d_site]
        return d_site

    def update_x_sig_s(self, s):
        """
        x_sig_sを決定したVM追加拠点sで更新する．
        """
        weight = 1.0 * self.vm_num[s] / (self.vm_num[s] + 1)
        for l in self.Graph.link_list:
            self.x_sig_s[s][l] *= weight
        for l in self.Graph.link_list:
            self.x_sig_s[s][l] += self.x_sig_allocated[s][l]
    
    def update_x_sig(self, s):
        """
        x_sigを更新する．
        """
        self.x_sig = copy.deepcopy(self.x_sig_solve[s])












if __name__ == '__main__':
    import Network
    import Model

    node     = 30
    site     = 5
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 20

    graph = Network.Topology(node, site, connects=3)
    model = Model.Model(graph)
    simu  = Simulator(graph, model, link_max, sig_max, sig_div, vm_add)
    for i in range(5):
        simu.solve()

    