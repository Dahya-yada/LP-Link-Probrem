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

    def __init__(self, o_graph, o_model, bw_max, ln_max, sig_trf_max, sig_div, vm_add):
        self.Graph       = o_graph
        self.Model       = o_model
        self.sig_trf_max = sig_trf_max
        self.sig_div     = sig_div
        self.sig_site    = sig_trf_max / sig_div
        self.bw_max      = bw_max
        self.ln_max      = ln_max
        self.try_max     = vm_add
        self.try_now     = 0

        self.L           = self.Graph.link_list
        self.La          = self.Graph.both_link_list
        self.N           = self.Graph.node_num
        self.SITE        = self.Graph.site_list

        self.x_sig       = {l: 0 for l in self.L}
        self.x_sig_n     = {s: {l: 0 for l in self.L} for s in self.SITE}
        self.x_sig_solve = {s: {l: 0 for l in self.L} for s in self.SITE}

        self.mn_sig       = {s: 0 for s in self.SITE}
        self.mb_sig       = {s: 0 for s in self.SITE}
        self.vm_num       = {s: 0 for s in self.SITE}
        self.std          = {n: 0 for n in range(self.try_max)}
    
    def solve(self, info=False):
        """
        1回だけ線形計画法を解く
        """
        for s in self.SITE:
            traffic = self.sig_site / self.Graph.site_num / (self.vm_num[s] + 1)
            ln_mat  = self.make_x_sig_n_matrix()
            bw_mat  = self.make_x_sig_matrix()

            self.Model.optimize(s, traffic, bw_mat, self.bw_max, ln_mat, self.ln_max)

            self.make_x_sig_solve(s)
            self.mb_sig[s] = int(self.Model.Mb.x)
            self.mn_sig[s] = int(self.Model.Mn.x)
        
        detect_s = self.detect_site()
        self.add_to_x_sig_n(detect_s)
        self.update_x_sig()
        std_no = self.calc_std()
        self.try_now += 1

        if info:
            info_str  = '#{0:02d},  '.format(self.try_now)
            info_str += '[site],{0:02d},  '.format(detect_s)
            info_str += '[Mb],{},  '.format(200 * self.mb_sig[s] / self.bw_max)
            info_str += '[Mn],{},  '.format(self.mn_sig[s])
            info_str += '[std],{0:.3f},{0:.3f},  '.format(self.std[self.try_now -1], std_no)
            print info_str



    def make_x_sig_n_matrix(self):
        """
        線形計画法に使う，[i,j] = 割当リンク数 のマトリックスを生成する．
        """
        tmp = {(i,j): self.ln_max for i in range(self.N) for j in range(self.N)}

        for l in self.La:
            tmp[l] = 0
        
        for s in self.SITE:
            for i,j in self.L:
                tmp[i,j] += self.x_sig_n[s][i,j]
                tmp[j,i] += self.x_sig_n[s][i,j]
        
        return tmp

    def make_x_sig_matrix(self):
        """
        線形計画法に使う，[i,j] = 割当リンク帯域 のマトリックスを生成する．
        """
        tmp = {(i,j): self.bw_max for i in range(self.N) for j in range(self.N)}

        for l in self.La:
            tmp[l] = 0

            for i,j in self.L:
                tmp[i,j] += self.x_sig[i,j]
                tmp[j,i] += self.x_sig[i,j]

        return tmp

    def make_x_sig_solve(self, s):
        """
        最適化結果をx_sig_solve[s]に保存する．
        """
        tmp = {(i,j): 0 for i,j in self.L}

        for d in self.Model.route:
            for i,j in tmp:
                if (i,j) in self.Model.route[s][d]:
                    tmp[i,j] += 1
                if (j,i) in self.Model.route[s][d]:
                    tmp[i,j] += 1
        
        self.x_sig_solve[s] = copy.deepcopy(tmp)
    
    def detect_site(self, info=False):
        """
        VM追加拠点を決定する．
        """
        li_eval  = {s: self.mb_sig[s] - self.vm_num[s] for s in self.SITE}
        add_site = max(li_eval.items(), key=lambda x: x[1])[0]
        self.vm_num[add_site] += 1

        if info:
            print "[SITE] {}".format(add_site)
            print "<DETECT ROUTE>"
            print self.Model.show_route(add_site)

        return add_site
    
    def add_to_x_sig_n(self, detect_s):
        """
        決定した経路をx_sig_num[detect_site]に追加する．
        """
        for l in self.x_sig_solve[detect_s]:
            self.x_sig_n[detect_s][l] += self.x_sig_solve[detect_s][l]
    
    def update_x_sig(self):
        """
        物理リンク帯域を表すx_sigを更新する．
        """
        tmp = {l: 0 for l in self.L}

        for s in self.Graph.site_list:
            if self.vm_num[s] == 0:
                continue
            trf = self.sig_site / self.Graph.site_num / self.vm_num[s]
            for l in self.L:
                tmp[l] += self.x_sig_n[s][l] * trf
        
        self.x_sig = copy.deepcopy(tmp)

    def calc_std(self, info=False):
        """
        物理リンクの使用帯域の標準偏差を求める．
        """
        std_no_s = numpy.std([self.x_sig[i,j] for i,j in self.x_sig if i not in self.Graph.site_list and j not in self.Graph.site_list])
        std = numpy.std(self.x_sig.values())
        self.std[self.try_now] = float(std)

        if info:
            print '[std dev] {}'.format(std)
        
        return std_no_s
    







if __name__ == '__main__':
    import Network
    import Model

    node         = 100
    site         = 10
    connect      = 3
    link_num_max = 100
    link_max     = 20 * 1024 * 1024
    sig_max      = 4 * 20000
    sig_div      = 20
    vm_add       = 50
    node         = 50

    graph = Network.Topology(node, site, connects=3, probability=0.3, types='powerlaw_cluster')
    model = Model.Model(graph)
    simu  = Simulator(graph, model, link_max, link_num_max, sig_max, sig_div, vm_add)

    graph.generate_images()

    for i in range(vm_add):
        simu.solve(info=True)
    print simu.vm_num
    for s in graph.site_list:
        print "[", s, "]"
        for l in graph.link_list:
            if simu.x_sig_n[s][l] > 0:
                print "{}: N:{} L:{}".format(l, simu.x_sig_n[s][l],simu.x_sig[l]),
        print ''
    print ''
    graph.generate_images(filename='Toporogy_2.svg', costList=simu.x_sig, first=False)
