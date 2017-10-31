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
        self.sig_site    = int(signal_traffic_max / signal_division)
        self.link_max    = bandwidth_max
        self.link_num    = link_num_max
        self.trial_num   = vm_add_num
        self.trial_now   = 0

        self.sig_m       = {s: 0 for s in self.Graph.site_list}
        self.sig_h       = {s: 0 for s in self.Graph.site_list}
        self.sig_std_dev = {n: 0 for n in range(self.trial_num)}
        self.vm_num      = {s: 0 for s in self.Graph.site_list}
        self.x_sig       = {l: 0 for l in self.Graph.link_list}
        self.x_sig_num   = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}
        self.x_sig_solve = {s: {l: 0 for l in self.Graph.link_list} for s in self.Graph.site_list}
    
    def solve(self, show_info=False):
        """
        1回だけ線形計画法を解く
        """
        for s in self.Graph.site_list:
            trf    = self.sig_site /self.Graph.site_num / (self.vm_num[s] + 1)
            matrix = self.make_x_sig_matrix()
            self.Model.optimize(s, self.link_num, matrix, 'n')
            self.make_x_sig_solve(s)
            self.sig_m[s] = int(self.Model.M.x)
            self.sig_h[s] = int(self.Model.H.x)
        d_site = self.decide_to_add_vm_site('n')
        self.add_link_to_x_sig_num(d_site)
        self.update_x_sig()
        stdxx = self.calc_dtandard_deviation('n')
        self.trial_now += 1

        if show_info:
            print "[{0:2d}],[Site],{1:2d}, [M],{2:2d}, [H],{3:2d}  [std_dev],{4}, {5}".format(
                self.trial_now,d_site, self.sig_m[d_site], self.sig_h[d_site],self.sig_std_dev[self.trial_now - 1], stdxx)


    def make_x_sig_matrix(self):
        """
        線形計画法に使う，[i,j] = 割当リンク数 のマトリックスを生成する．
        """
        n   = self.Graph.node_num
        tmp = {(i,j): self.link_num for i in range(n) for j in range(n)}

        for l in self.Graph.both_link_list:
            tmp[l] = 0

        for s in self.Graph.site_list:
            for i,j in self.Graph.link_list:
                tmp[i, j] += int(self.x_sig_num[s][i,j])
                tmp[j, i] += int(self.x_sig_num[s][i,j])

        return tmp

    def make_x_sig_solve(self, s):
        """
        最適化結果をx_sig_solve[s]に保存する．
        """
        tmp = {(i,j): 0 for i,j in self.Graph.link_list}

        for d in self.Model.route:
            for i,j in tmp:
                if (i,j) in self.Model.route[s][d]:
                    tmp[i,j] += 1
                if (j,i) in self.Model.route[s][d]:
                    tmp[i,j] += 1

        self.x_sig_solve[s] = copy.deepcopy(tmp)
    
    def decide_to_add_vm_site(self, show_info='yes'):
        """
        VM追加拠点を決定する．
        """
        mpv    = {s: self.sig_m[s] - self.vm_num[s] for s in self.Graph.site_list} 
        detect = max(mpv.items(),key=lambda x: x[1])[0]
        self.vm_num[detect] += 1

        if show_info == 'yes' or show_info == 'y':
            print '========== [DETECT ROUTE] =========='
            self.Model.show_route(detect)

        return detect

    def add_link_to_x_sig_num(self, decide_site):
        """
        決定した経路をx_sig_num[detect_site]に追加する．
        """
        for l in self.x_sig_solve[decide_site]:
            self.x_sig_num[decide_site][l] += self.x_sig_solve[decide_site][l]

    def update_x_sig(self):
        """
        物理リンク帯域を表すx_sigを更新する．
        """
        tmp = {l: 0 for l in self.Graph.link_list}

        for s in self.Graph.site_list:
            if self.vm_num[s] == 0:
                continue
            sig_vm = self.sig_site /self.Graph.site_num / self.vm_num[s]
            for l in self.Graph.link_list:
                tmp[l] += self.x_sig_num[s][l] * sig_vm

            self.x_sig = copy.deepcopy(tmp)

    def calc_dtandard_deviation(self, show_info='yes'):
        """
        物理リンクの使用帯域の標準偏差を求める．
        """
        std_dev_xx = numpy.std([self.x_sig[l] for l in self.Graph.link_list if self.x_sig[l] != 0])
        std_dev = numpy.std(self.x_sig.values())
        self.sig_std_dev[self.trial_now] = std_dev

        if show_info == 'yes' or show_info == 'y':
            print '========[STANDARD DEVIATION]========'
            print "M", self.Model.M
            print std_dev
            print std_dev_xx
            print ''
        
        return std_dev_xx






if __name__ == '__main__':
    import Network
    import Model

    node         = 50
    site         = 5
    connect      = 3
    link_num_max = 100
    link_max     = 20 * 1024 * 1024
    sig_max      = 4 * 20000
    sig_div      = 20
    vm_add       = 50

    graph = Network.Topology(node, site, connects=3, probability=0.5, types='powerlaw_cluster')
    model = Model.Model(graph)
    simu  = Simulator(graph, model, link_max, link_num_max, sig_max, sig_div, vm_add)

    graph.generate_images()

    for i in range(vm_add):
        simu.solve(show_info=True)
    print simu.vm_num
    for s in graph.site_list:
        print "[", s, "]"
        for l in graph.link_list:
            if simu.x_sig_num[s][l] > 0:
                print "{}: N:{} L:{}".format(l, simu.x_sig_num[s][l],simu.x_sig[l]),
        print ''
    print ''
    graph.generate_images(filename='Toporogy_2.svg', costList=simu.x_sig, first=False)
