# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import numpy
import Utils

class Simulator(object):
    """
    1回だけVMを割り当てるシミュレーションを実行します．
    すべての拠点へVM配置及び仮想リンク割当を行い，目的関数の値が最大の拠点と仮想リンク経路を求めます．
    """

    def __init__(self, graph, model, id_space, lb_max, ln_max, max_sig_trf, max_cp_trf, vm_add_num):
        self.graph    = graph
        self.model    = model
        self.id_space = id_space
        self.lb_max   = lb_max
        self.ln_max   = ln_max
        self.t_sig    = max_sig_trf
        self.t_cp     = max_cp_trf
        self.try_n    = 0
        self.try_m    = vm_add_num

        self.x_bw       = {l: 0 for l in self.graph.link_list}
        self.x_num      = {l: 0 for l in self.graph.link_list}
        self.x_sig_num  = {s: {l: 0 for l in self.graph.link_list} for s in self.graph.site_list}
        self.x_cp_route = {}
        self.vm_num     = {s: 0 for s in self.graph.site_list}

        self.obj_val    = {n: 0 for n in range(vm_add_num)}
        self.std_bw     = {n: 0 for n in range(vm_add_num)}
        self.std_num    = {n: 0 for n in range(vm_add_num)}
        self.use_link   = {n: 0 for n in range(vm_add_num)}

    def solve(self, info=False):
        """
        シミュレーションを実行します．
        """
        timer1 = Utils.Timer()

        for s in self.graph.site_list:
            timer2 = Utils.Timer()
            self.model.optimize(s, self.get_sig_traffic(s, is_next=True), self.get_cp_traffic(is_next=True)[s],
                                self.get_lb_matrix(), self.lb_max, self.get_ln_matrix(), self.ln_max,
                                self.get_node_spent_matrix())
            
   

    def get_sig_traffic(self, s, is_next=False):
        """
        sから他の拠点に転送する信号トラヒックを取得します．
        """
        if is_next:
            trf = self.t_sig / (self.vm_num[s] + 1) / self.graph.site_num
        else:
            trf = self.t_sig / self.vm_num[s] / self.graph.site_list_num
        return trf

    def get_cp_traffic(self, vm_id=None, is_next=False):
        """
        vm_idのMVが他の拠点に転送する複製トラヒックを取得します．
        """
        node_list = self.id_space.get_right_node_by_id(vm_id)
        node_all  = sum(node_list.values())
        t_list  = {s: 0 for s in self.graph.site_list}

        for s in t_list:
            if node_list[s] > 0:
                trf_ratio = 1.0 / self.graph.site_num
            else:
                trf_ratio = 1.0 * node_list[s] / node_all
            if is_next:
                trf = trf_ratio * self.t_cp / (self.vm_num[s] + 1)
            else:
                trf = trf_ratio * self.t_cp / self.vm_num[s]
            t_list[s] += trf
        return t_list

    def get_lb_matrix(self):
        """
        線形計画法に必要な使用帯域マトリックス(lb_now)を生成します．
        """
        lb_mat = {l: self.lb_max for l in self.graph.both_link_list}
        for i, j in self.graph.link_list:
            lb_mat[i,j] = 0
            lb_mat[j,i] = 0
        for i, j in self.graph.link_list:
            lb_mat[i,j] += self.x_bw[i,j]
            lb_mat[j,i] += self.x_bw[i,j]
        return lb_mat


    def get_ln_matrix(self):
        """
        線形計画法に必要な消費リンク数を表すマトリックス(ln_now)を生成します．
        """
        ln_mat = {l: self.ln_max for l in self.graph.both_link_list}
        for i, j in self.graph.link_list:
            ln_mat[i,j] = 0
            ln_mat[j,i] = 0
        for i, j in self.graph.link_list:
            ln_mat[i,j] = self.x_num[i,j]
            ln_mat[j,i] = self.x_num[i,j]
        return ln_mat

    def get_node_spent_matrix(self):
        """
        数理計画法に必要なノードに到達したトラヒックを表すマトリックス(nw_node_now)を生成します．
        """
        node_mat = {n: 0 for n in range(self.graph.node_num)}
        for i, j in self.graph.link_list:
            node_mat[j] += self.x_bw[i,j]

    def add_x_sig_solve(self, s, solve_data):
        """
        最適化した決定変数Xの値を引数solve_dataに追加します．
        """
        d_new = {(i,j): 0 for i,j in self.graph.link_list}
        for d in self.model.route_sig:
            for i, j in d_new:
                if (i, j) in self.model.route_sig[s][d]:
                    d_new[i, j] += 1
                if (i, j) in self.model.route_sig[s][d]:
                    d_new[i, j] += 1
        solve_data[s] = copy.deepcopy(d_new)

    def add_x_cp_solve(self, s, solve_data):
        """
        最適化した決定変数Yの値を引数solve_dataに追加します．
        """
        d_new = {}
        for d in self.model.route_cp:
            if s == d:
                continue
            d_new[d] = copy.deepcopy(self.model.route_cp[s][d])
        solve_data[s] = copy.deepcopy(d_new)

    def add_decision_var_solve(self, s, o_data, l_data, n_data):
        """
        最適化した決定変数の値をo_data, l_data, n_dataに代入します．
        """
        o_data[s] = float(self.model.model.objval)
        l_data[s] = float(self.model.L)
        n_data[s] = float(self.model.N)

    def decide_site(self, objval_data, info=False):
        """
        最適化した目的関数の値からVM追加拠点を決定します．
        """
        eval_list = {s: objval_data[s] - self.vm_num[s] for s in self.graph.site_list}
        decided   = max(eval_list.items(), key=lambda x: x[1])[0]

        if info:
            print "DECIDED SITE",
            Utils.StrOut.green('  [SITE]: ', end='')
            print decided
            Utils.StrOut.green('  [OBJ VAL]:  ', end='')
            print (eval_list[decided])

        return decided 

    def update_x_sig_num(self, s, solve_data):
        """
        solve_dataに基づいてインスタンス変数x_sig_numを更新します．
        """
        for l in self.graph.link_list:
            self.x_sig_num[s][l] += solve_data[s][l]

    def update_x_cp_route(self, s, vm_id, solve_data):
        """
        solve_dataに基づいてインスタンス変数x_cp_numを更新します．
        """
        for d in solve_data:
            self.x_cp_route[(vm_id, s, d)] = solve_data[s][d]

    def update_x_bw(self):
        """
        インスタンス変数x_bwを更新します．
        """
        d_new = {l: 0 for l in self.graph.link_list}
        # Traffic of dispatch
        for s in self.x_sig_num:
            t = self.get_sig_traffic(s)
            for l in d_new:
                d_new[l] += self.x_sig_num[s][l] * t
        for vi, s, d in self.x_cp_route:
            t = self.get_cp_traffic(vi)
            for i, j in self.x_cp_route[(vi, s, d)]:
                if (i, j) in d_new:
                    d_new[i, j] += t
                if (j, i) in d_new:
                    d_new[j,i] += t
        self.x_bw = copy.deepcopy(d_new)

    def update_x_num(self):
        """
        インスタンス変数x_numを更新します．
        """
        d_new = {l: 0 for l in self.graph.link_list}
        for s in self.x_sig_num:
            for l in d_new:
                d_new[l] += self.x_sig_num[s][l]
        for idx in self.x_cp_route:
            for i, j in self.x_cp_route[idx]:
                if (i, j) in d_new:
                    d_new[i, j] += 1
                if (j, i) in d_new:
                    d_new[j, i] += 1
        self.x_num = copy.deepcopy(d_new)

    def update_use_link(self, t):
        """
        試行回数t回目の使用物理リンク数を更新します．
        """
        for l in self.x_num:
            if self.x_num[l] > 0:
                self.use_link[t] += 1

    def update_std(self, t, info=False):
        """
        試行回数t回目の各標準偏差を更新します．
        """
        std_b = numpy.std(self.x_bw.values())
        std_n = numpy.std(self.x_num.values())
        self.std_bw[t]  = float(std_b)
        self.std_num[t] = float(std_n)

        if info:
            print 'STANDARD DEVIATION',
            Utils.StrOut.green('  [BAND]: ', end='')
            print std_b,
            Utils.StrOut.green('  [NUM]: ', end='')
            print std_n


if __name__ == '__main__':
    import Network
    import Model
    import IdSpace

    node = 50
    site = 10
    conn =  3
    id_space_bit_len = 128
    id_space_vm_node = 20
    lb_max  = 1024 * 1024 * 20
    ln_max  = 50
    sig_trf = 4 * 200000 / 3600
    cpy_trf = 1 * 200000 / 3600
    add_num = 100

    graph     = Network.Topology(node, site, conn, types='random_regular')
    model     = Model.Model(graph)
    ids       = IdSpace.Space(graph.site_list, id_space_bit_len, id_space_vm_node)
    simurator = Simulator(graph, model, ids, lb_max, ln_max, sig_trf, cpy_trf, add_num)

    simurator.solve()