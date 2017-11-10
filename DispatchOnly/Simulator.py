# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import numpy
import time

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
        self.x_sig_num   = {l: 0 for l in self.L}
        self.x_sig_node  = {n: 0 for n in range(self.N)} 
        self.x_sig_n     = {s: {l: 0 for l in self.L} for s in self.SITE}
        self.x_sig_solve = {s: {l: 0 for l in self.L} for s in self.SITE}

        self.mn_sig       = {s: 0 for s in self.SITE}
        self.mb_sig       = {s: 0 for s in self.SITE}
        self.nn_sig       = {s: 0 for s in self.SITE}
        self.objval_sig   = {s: 0 for s in self.SITE}
        self.vm_num       = {s: 0 for s in self.SITE}
        self.std          = {n: 0 for n in range(self.try_max)}
        self.std_num      = {n: 0 for n in range(self.try_max)}
        self.link_use     = {n: 0 for n in range(self.try_max)}
    
    def solve(self, info=False):
        """
        1回だけ線形計画法を解く
        """
        time_start  = time.time()

        for s in self.SITE:
            traffic = self.sig_site / self.Graph.site_num / (self.vm_num[s] + 1)
            ln_mat  = self.make_x_sig_n_matrix()
            bw_mat  = self.make_x_sig_matrix()

            self.Model.optimize(s, traffic, bw_mat, self.bw_max, ln_mat, self.ln_max, self.x_sig_node)

            self.make_x_sig_solve(s)
            self.mb_sig[s]     = int(self.Model.Mb.x)
            self.mn_sig[s]     = int(self.Model.Mn.x)
            self.nn_sig[s]     = int(self.Model.NN.x)
            self.objval_sig[s] = float(self.Model.model.objVal)
        
        detect_s = self.detect_site()
        self.add_to_x_sig_n(detect_s)
        self.update_x_sig()
        self.update_x_sig_node()
        self.update_link_use()
        self.calc_std()
        self.try_now += 1

        time_proc = time.time() - time_start

        if info:
            info_str  = '#{0:02d},  '.format(self.try_now)
            info_str += '[site],{0:02d},  '.format(detect_s)
            info_str += '[Mb],{},  '.format(100 * self.mb_sig[s] / self.bw_max)
            info_str += '[Mn],{},  '.format(100 * self.mn_sig[s] / self.ln_max)
            info_str += '[MN],{},  '.format(100 * self.nn_sig[s] / self.bw_max)
            info_str += '[OBJ],{0:3.3f},  '.format(self.objval_sig[s])
            info_str += '[std],{0:5.3f}, {1:2.3f},  '.format(self.std[self.try_now -1], self.std_num[self.try_now - 1])
            info_str += '[time (s)],{0:.3f}'.format(time_proc)
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
        # li_eval  = {s: (self.mb_sig[s] / self.bw_max * 200) + self.mn_sig[s]  - self.vm_num[s] for s in self.SITE}
        # li_eval  = {s: (self.mb_sig[s] / self.bw_max * 200) - self.vm_num[s] for s in self.SITE}
        li_eval  = {s: self.objval_sig[s] - self.vm_num[s] for s in self.SITE}
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
        tmp_b = {l: 0 for l in self.L}
        tmp_n = {l: 0 for l in self.L}

        for s in self.Graph.site_list:
            if self.vm_num[s] == 0:
                continue
            trf = self.sig_site / self.Graph.site_num / self.vm_num[s]
            for l in self.L:
                tmp_b[l] += self.x_sig_n[s][l] * trf
                tmp_n[l] += self.x_sig_n[s][l]
        
        self.x_sig     = copy.deepcopy(tmp_b)
        self.x_sig_num = copy.deepcopy(tmp_n)
    
    def update_x_sig_node(self):
        """
        NWノードに到達したトラヒックの合計を表すx_sig_nodeを更新する．
        """
        tmp = {n: 0 for n in range(self.N)}

        for s in self.Graph.site_list:
            if self.vm_num[s] == 0:
                continue
            trf = self.sig_site / self.Graph.site_num / self.vm_num[s]
            for i,node in self.L:
                tmp[node] += self.x_sig_n[s][i, node] * trf
            
            self.x_sig_node = copy.deepcopy(tmp)
    
    def update_link_use(self):
        """
        使用された物理リンク数を更新します．
        """
        for l in self.x_sig_num:
            if self.x_sig_num[l] > 0:
                self.link_use[self.try_now] += 1


    def calc_std(self, info=False):
        """
        物理リンクの使用帯域の標準偏差を求める．
        """
        std_n = numpy.std(self.x_sig_num.values())
        std   = numpy.std(self.x_sig.values())
        self.std_num[self.try_now] = float(std_n)
        self.std[self.try_now] = float(std)

        if info:
            print '[std dev] {}'.format(std)
            print '[std_dev_num] {}'.format(std_n)
    







if __name__ == '__main__':
    import Network
    import Model

    node         = 50
    site         = 10
    connect      = 3
    link_num_max = 100
    link_max     = 20 * 1024 * 1024
    sig_max      = 4 * 20000
    sig_div      = 20
    vm_add       = 100

    graph = Network.Topology(node, site, connects=connect, probability=0.3, types='powerlaw_cluster')
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
