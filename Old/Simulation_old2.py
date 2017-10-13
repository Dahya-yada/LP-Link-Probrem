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
        self.Data  = o_data
        self.Model = o_model
        self.Graph = o_graph

        self.x_sig_site    = {s: {l: 0 for l in o_data.graph.link_list} for s in o_graph.site_list}
        self.x_sig_tmp     = {s: {l: 0 for l in o_data.graph.link_list} for s in o_graph.site_list}
        self.x_sig_tmp_one = {s: {l: 0 for l in o_data.graph.link_list} for s in o_graph.site_list}
        self.x_sig_solved  = {s: {l: 0 for l in o_data.graph.link_list} for s in o_graph.site_list}
        self.sig_lb_tmp    = copy.deepcopy(self.Data.signal_lb)
        self.add_vm_site   = 0
    

    def solve(self):
        """
        1回だけすべての拠点に対し，線形計画法を解く
        """
        print "[solve]",
        self.change_signal_bandwidth()
        
        for s in self.Graph.site_list:
            self.change_signal_bandwidth_for_vm(s)
            self.change_signal_vm(s)
            self.Model.make_model(s, self.make_x_matrix(s))
            self.Model.MODEL.optimize()
            print "[{}]M{} H{}".format(s, self.Model.M.x, self.Model.H.x),
            self.copy_result_to_solved_x(s)
            print "*",
        
        self.calc_add_vm_site()
        self.update_datas()


    def change_signal_bandwidth(self):
        """
        LBへの信号量が増減した場合，割当済みリンク帯域を変更する．
        """
        if self.sig_lb_tmp != self.Data.signal_lb:
            increase = self.Data.signal_lb / self.sig_lb_tmp

            for s in self.Graph.site_list:
                for l in self.Graph.link_list:
                    self.x_sig_tmp[s][l] = self.x_sig_tmp[s][l] * increase
            self.x_sig_site = copy.deepcopy(self.x_sig_tmp)
            self.x_sig_solved = copy.deepcopy(self.x_sig_tmp)
    
    def change_signal_bandwidth_for_vm(self, s):
        """
        VM追加のために，sからの割当済み帯域を変更する．
        """
        self.x_sig_tmp = copy.deepcopy(self.x_sig_site)
        increase = self.Data.vm_num[s] / (self.Data.vm_num[s] + 1)

        for l in self.Graph.link_list:
            self.x_sig_tmp[s][l] = self.x_sig_tmp[s][l] * increase
            if  self.x_sig_tmp[s][l] > 0:
                print "change band:", self.x_sig_tmp[s][l]

    def change_signal_vm(self, s):
        """
        sに新しく配置されるVMが担当する信号量を決定する．
        """
        self.Data.signal_vm = self.Data.signal_lb / self.Graph.site_num / (self.Data.vm_num[s] + 1)
        #print "sig traffic:", self.Data.signal_vm

    def make_x_matrix(self, s):
        """
        無効リンクを含むリンクマトリックスを生成する．
        """
        matrix = {(i, j): self.Data.bandwidth_max for i in range(self.Graph.node_num) for j in range(self.Graph.node_num)}

        for l in self.Graph.both_link_list:
            matrix[l[0], l[1]] = 0

        for l in self.Graph.link_list:
            matrix[l[0], l[1]] = copy.deepcopy(self.x_sig_tmp[s][l])
            matrix[l[1], l[0]] = copy.deepcopy(self.x_sig_tmp[s][l])
        return matrix

    def copy_result_to_solved_x(self, s):
        """
        最適化結果をx_sig_solved[s]にコピーします．
        """
        self.x_sig_solved[s] = copy.deepcopy(self.x_sig_tmp[s])

        for l in self.Graph.link_list:
            for d in self.Graph.site_list:
                self.x_sig_solved[s][l] += self.Model.X[d, l[0], l[1]].x * self.Data.signal_vm
                self.x_sig_solved[s][l] += self.Model.X[d, l[1], l[0]].x * self.Data.signal_vm
        
        for l in self.Graph.link_list:
            for d in self.Graph.site_list:
                self.x_sig_tmp_one[s][l] += self.Model.X[d, l[0], l[1]].x * self.Data.signal_vm
                self.x_sig_tmp_one[s][l] += self.Model.X[d, l[1], l[0]].x * self.Data.signal_vm 
    
    def calc_add_vm_site(self, types='std_dev'):
        """
        最適化結果から，VMを追加する拠点を求める．
        """
        if types == 'std_dev':
            std_dev = {s: numpy.std(self.x_sig_solved[s].values()) for s in self.Graph.site_list}
            min_dev_site = min(std_dev.items(), key=lambda x: x[1])[0]
            print "\n[min_dev_site] <", min_dev_site, "> =", std_dev[min_dev_site]
            self.add_vm_site = min_dev_site
            self.Data.std_dev[self.Data.try_now] = min_dev_site
    
    def update_datas(self):
        """
        最適化結果に基づきデータを更新する．
        """
        self.x_sig_site[self.add_vm_site] = copy.deepcopy(self.x_sig_tmp[self.add_vm_site])
        for l in self.Graph.link_list:
            self.x_sig_site[self.add_vm_site][l] += self.x_sig_tmp_one[self.add_vm_site][l]

        self.Data.x_sig = {l: 0 for l in self.Graph.link_list}
        for s in self.Graph.site_list:
            for l in self.Graph.link_list:
                self.Data.x_sig[l] += self.x_sig_site[s][l]
        
        self.x_sig_solved  = copy.deepcopy(self.x_sig_site)
        self.x_sig_tmp = copy.deepcopy(self.x_sig_site)
        self.Data.vm_num[self.add_vm_site] += 1





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
    sim.solve()
