# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import gurobipy as grb

class Model(object):
    """
    線形計画法モデルオブジェクト
    """
    def __init__(self, graph):
        self.o_graph = graph
        self.o_model = grb.Model('LP_MODEL')
        self.X       = 0
        self.M       = 0
        self.H       = 0
        self. non_loop_route = {}

    def make_model(self, s, link_num_max, link_num_now):
        # GUROBIオブジェクト
        self.o_model = grb.Model('LP_MODEL')
        self.o_model.setParam('OutputFlag', False)
        # 添字
        D  = self.Graph.site_list
        I  = range(self.Graph.node_num)
        J  = range(self.Graph.node_num)
        # リンクセット
        ij_graph = self.o_graph.both_link_list
        ij_set   = [(i,j)   for i in I for J in J if i != j]
        di_set   = [(d,i)   for d in D for i in I if s != d]
        dij_set  = [(d,i,j) for d in D for i in I for j in J if s != d and i != j]
        # 定数
        ln_max = link_num_max
        ln_now = link_num_now
        # 変数
        v_x = {(d,i,j): self.o_model.addVar(vtype='B', name='x.{}:{}.{}'.format(d,i,j) for D in d  for I in i for j in J)}
        v_m = self.o_model.addVar(vtype='I', name='M')
        v_h = self.o_model.addVar(vtype='I', name='H')
        # メンバから参照可能にする
        self.X = v_x
        self.M = v_m
        self.H = v_h

        # モデルのアップデート
        self.o_model.update()

        # 目的関数
        self.o_model.setObjective(M + H , grb.GRB.MINIMIZE)

        # 制約: フロー保存
        for d, i in di_set:
            if i == s:
                self.o_model.addConstr(grb.quicksum(v_x[d,i,j] for j in J) - grb.quicksum(v_x[d,j,i] for j inJ) ==  1,
                                       "const:frow:s_{}".format(d))
            if i == d:
                self.o_model.addConstr(grb.quicksum(v_x[d,i,j] for j in J) - grb.quicksum(v_x[d,j,i] for j inJ) == -1,
                                       "const:frow:d_{}".format(d))
            if i != s and i != d:
                self.o_model.addConstr(grb.quicksum(v_x[d,i,j] for j in J) - grb.quicksum(v_x[d,j,i] for j inJ) ==  0,
                                       "const:flow:i_{}.{}".format(i,d))

        # 制約: リンク数制限
        for d, i, j in dij_set:
            self.o_model.addConstr(v_x[d,i,j] + ln_now[i,j] <= ln_max)
        
        # 制約: 各リンクの本数の最大
        for d in D:
            if s == d:
                continue
            self.o_model.addConstr(grb.quicksum(v_x[d,i,j] + ln_now for i,j in ij_graph) <= M, "const:M")
        
        # 制約: ホップ数
        for d in D:
            if s == d:
                continue
            self.o_model.addConstr(grb.quicksum(v_x[d,i,j] for i,j in ij_set) <= H, "const:H")
    
    def make_route(self, s):
        allocate = {d:[(i,j) for i,j in self.o_graph.both_link_list if self.X[d,i,j].x > 0] for d in self.o_graph.site_list}
        route ={d:list() for d in self.o_graph.site_list}

        for d in route:
            tmp = []
            j = d
            for i in range(self.o_graph.node_mun):
                if (i,j) in route[d]:
                    tmp[d].append((i,j))
                    j = i
                if i == s:
                    break
            route[d] = copy.deepcopy(tmp.reverse())
                    


        



