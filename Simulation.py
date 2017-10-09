# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326

import copy
import numpy

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
        """
        一度だけ線形計画問題を解きます．これに基づき，最小の標準偏差を持つような，新しい仮想リンクと拠点を決定します．
        """
        S            = self.DATA.graph.site_list
        result_links = {k: 0 for k in S}

        self.detect_signal_bandwidth()
        self.copy_site_x_tmp_to_solve_x()

        for s in S:
            self.MODEL.make_model()
            self.MODEL.MODEL.optimize()
            result_links[s] = self.make_result_link_dic()
        
        min_dev_site = self.calc_std_dev(result_links)
        copy_result_to_site_x_tmp(min_dev_site, result_links)
        self.DATA.vm_num[min_dev_site] += 1
        make_x_sig()
        

            
    
    def detect_signal_bandwidth(self):
        """
        VM追加のために，sites_x_tmp[vm_add_num][site_num][link]の値を更新する．
        VM追加のために，signal_nowを更新します．
        更新する値は，vm_num[s] / (all_vm_num + 1) * site_x_tmp[][][] です．
        """
        d_link_list   = self.DATA.graph.link_list
        d_site_list   = self.DATA.graph.site_list
        d_sites_x_tmp = self.DATA.sites_x_tmp
        d_vm_num      = self.DATA.vm_num
        d_signal_site = self.DATA.signal_site
        d_signal_now  = self.DATA.signal_now
        d_try_now     = self.DATA.try_now

        all_vm = sum(self.DATA.vm_num.values())

        if all_vm > 0:
            d_signal_site = (d_vm_num + 1) / all_vm * d_signal_now

            for s in d_site_list:
                for i in range(d_try_now):
                    for l in d_link_list:
                        if d_sites_x_tmp[i][s][l] > 0:
                            d_sites_x_tmp[i][s][l] =  (d_vm_num[s] / (all_vm + 1)) * d_sites_x_tmp[i][s][l]
        else:
            d_signal_site = d_signal_now
    
    def copy_site_x_tmp_to_solve_x(self):
        """
        site_x_tmpの内容をsolve_xにコピーします．
        """
        I = range(self.DATA.try_now)
        S = self.DATA.graph.site_list
        L = self.DATA.graph.link_list

        self.DATA.solve_x = self.DATA.make_link_matrix()

        for i in I:
            for s in S:
                for l in L:
                    self.DATA.solve_x[l] += self.DATA.sites_x_tmp[i][s][l]
                    self.DATA.solve_x[l[1], l[0]] += self.DATA.sites_x_tmp[i][s][l[1], l[0]]
    
    def copy_result_to_site_x_tmp(self, s, result_links):
        """
        新しい仮想リンク経路をsite_x_tmpにコピーする．
        """
        L     = self.DATA.graph.link_list
        t_num = self.DATA.try_num
        d_site_x_tmp = self.DATA.sites_x_tmp
        
        for l in L:
            d_site_x_tmp[t_num][s][l[0] ,l[1]] = result_links[s][l[0],l[1]]

    
    def make_result_link_dic(self):
        """
        ソルバーが求めた仮想リンク経路のディクショナリを生成する．
        """
        D   = self.DATA.graph.site_list
        L   = self.DATA.graph.link_list
        dic = self.DATA.graph.make_link_dict

        for d in D:
            for l in L:
                dic[l[0], l[1]] += self.MODEL.X[d, l[0], l[1]].x * self.DATA.signal_site
                dic[l[1], l[0]] += self.MODEL.X[d, l[1], l[0]].x * self.DATA.signal_site
        return dic

        def calc_min_std_dev(self, result_links):
            """
            求めた仮想リンク経路から，物理リンクの使用帯域の標準偏差が最小の拠点を求めます．
            """
            S           = self.DATA.graph.site_list
            D           = self.DATA.graph.link_list
            result      = copy.deepcopy(result_links)
            std_dev_tmp = {k: 0 for k in self.DATA.graph.site_list}

            for s in S:
                for l in L:
                    result[s][l] += self.DATA.x_sig[l]

            for s in S:
                std_dev_tmp[s] = numpy.std(result[s].values())
            min_dev_site = std_dev_tmp.items(), key=lambda x:x[1])[0]

            self.DATA.std_dev[self.DATA.try_now] = std_dev_tmp[min_dev_site]

            return min_dev_site
        
        def make_x_sig(self)
            I = range(self.DATA.try_now)
            S = self.DATA.graph.site_list
            L = self.DATA.graph.link_list

            self.DATA.x_sig = self.DATA.make_link_dict()

            for i in I:
                for s in S:
                    for l in L:
                        self.DATA.x_sig[l] += self.DATA.sites_x_tmp[i][s][l[0], l[1]]
                        self.DATA.x_sig[l] += self.DATA.sites_x_tmp[i][s][l[1], l[0]]



    




        











    







    def solve(self):
        for s in self.DATA.graph.site_list:
            self.MODEL.model(s)
            self.MODEL.MODEL.optimize()
            write_resolve_to_sitex_x_temp()
    
        min_dev_site = self.calc_std_dev()
        self.DATA.sites_x_sig[s] = copy.deepcopy(self.DATA.sites_x_tmp[s])
        self.DATA.sites_x_tmp    = self.make_site_link_dict() 

        self.DATA.vm_num[min_dev_site] += 1

    def detect_signal_bandwidth(self):
        all_vm = sum(self.DATA.vm_num.values())
        if all_vm > 0:
            for s in self.DATA.graph.site_list:
                self.DATA.signal_site[s] = (self.DATA.vm_num + 1) / all_vm * self.DATA.signal_now
            
    
    def write_resolve_to_sitex_x_temp(self):
        D = self.DATA.graph.site_list
        L = self.DATA.graph.both_link_list
        for d in D:
            for l in L:
                if (l[0], l[1]) in self.DATA.sites_x_tmp:
                    self.DATA.sites_x_tmp[s][l[0], l[1]] += self.MODEL.X[d, l[0], l[1]].x * self.DATA.signal_now
                if (l[1], l[0]) in self.DATA.sites_x_tmp:
                    self.DATA.sites_x_tmp[s][l[1], l[0]] += self.MODEL.X[d, l[0], l[1]].x * self.DATA.signal_now

    def calc_std_dev(self):
        std_dev_tmp = {k: 0 for k in self.DATA.graph.site_list}

        for s in self.DATA.graph.site_list:
            std_dev_tmp[s] = numpy.std(self.DATA.sites_x_tmp[s].values())
    
        min_dev_site = std_dev_tmp.items(), key=lambda x:x[1])[0]
        self.DATA.std_dev[self.DATA.try_now] = std_dev_tmp[min_dev_site]

        return min_dev_site

    








# MAIN
if __name__ == '__main__':
    node     = 100
    site     = 10
    connect  = 3
    link_max = 20 * 1024 * 1024
    sig_max  = 4 * 20000
    sig_div  = 20
    vm_add   = 200

    graph = Network.Topology(node, site, connects=3)
    data  = Data.Data(graph, link_max, sig_max, sig_div, vm_add)
    model = LpModel.Model(data)
    simu  = Simulation(data,model)
    simu.solve()

