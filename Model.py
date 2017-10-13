# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import gurobipy as grb

class Model(object):
    """
    線形計画法モデルオブジェクト
    """
    def __init__(self, graph):
        self.Graph = graph
        self.MODEL = grb.Model('LP_MODEL')
        self.X     = 0
        self.M     = 0
        self.H     = 0

    def make_model(self, s, link_max, link_used, traffic):
        # GUROBIオブジェクト
        self.MODEL = grb.Model('LP_MODEL')
        self.MODEL.setParam('OutputFlag', False)
        # 添字
        D  = self.DATA.graph.site_list
        I  = range(self.Graph.node_num)
        J  = range(self.Graph.node_num)
        # 定数
        #Tsig = self.DATA.signal_vm
        T    = traffic
        Lmax = link_max
        Luse = link_used
        # 変数
        X = {(d, i, j): self.MODEL.addVar(vtype='B', name='x.{}.{}.{}'.format(d,i,j)) for j in J for i in I for d in D}
        M = self.MODEL.addVar(vtype='I', name='M')
        H = self.MODEL.addVar(vtype='I', name='H')

        self.X = X
        self.M = M
        self.H = H

        # for l in self.DATA.graph.both_link_list:
        #     print "{}:{},".format(l, Luse[l]),
        # print ""

        # モデルのアップデート
        self.MODEL.update()

        # 目的関数
        self.MODEL.setObjective(M + H, grb.GRB.MINIMIZE)

        # 制約式
        for d in D:
            if s == d:
                continue
            for i in I:
                if i == s:
                    self.MODEL.addConstr(grb.quicksum(X[d,i,j] for j in J) - grb.quicksum(X[d,j,i] for j in J) == 1,
                                         'CONST::folw:s')
                if i == d:
                    self.MODEL.addConstr(grb.quicksum(X[d,i,j] for j in J) - grb.quicksum(X[d,j,i] for j in J) == -1,
                                         'CONST::folw:d')
                if i != s and i != d:
                    self.MODEL.addConstr(grb.quicksum(X[d,i,j] for j in J) - grb.quicksum(X[d,j,i] for j in J) == 0,
                                         'CONST::folw:{}'.format(i))

        for d in D:
            if s == d:
                continue
            for i in I:
                for j in J:
                    if i == j:
                        continue
                    self.MODEL.addConstr(X[d,i,j] * T >= 0, 
                                         'CONST::traff_x.{}.{}.{}>=0'.format(d,i,j))
                    self.MODEL.addConstr(X[d,i,j] * T + Luse[i,j] <= Lmax, 
                                         'CONST::traff_x.{}.{}.{}<=MAX'.format(d,i,j))

        # for i in I:
        #     for j in J:
        #         if Luse[i,j] >= Lmax:
        #             continue
        #         # self.MODEL.addConstr(grb.quicksum(X[d,i,j] for d in D if s != d) + Luse[i,j] <= M, 
        #         #                      'CONST::x.{}.{} <= M'.format(i,j))
        #         self.MODEL.addConstr(grb.quicksum(X[d,i,j] * Tsig for d in D if s != d) + Luse[i,j] <= M,
        #                             'CONST::x.{}.{}*T<=M'.format(i,j))
        for d in D:
            if s == d:
                continue
            self.MODEL.addConstr(grb.quicksum(X[d, i, j] * T + Luse[i, j] for i in I for j in J if i==j) <= M,
                                 'CONST::X_{}<=M'.format(d)) 
        
        for i in I:
            for j in J:
                self.MODEL.addConstr(grb.quicksum(X[d,i,j] for d in D if s != d) <= H, 'CONST::x.{}.{}<=H'.format(i,j))
    
    def show_route(self, s):
        """
        構築した経路を表示する．
        """
        idx = [(i,j) for i in range(self.Graph.site_list) for j in range(self.Graph.node_num)]
        for d in self.Graph.site_list:
            if d == s:
                continue
            is_link = {}
            for i in idx:
                if self.X[d,idx[0],idx[1]] > 0:
                    is_link[idx] = 1
            p = s
            while(True):
                for i in range(self.Graph.site_list):
                    if (p,i) in is_link:
                        print "({}, {})".format(s,i),
                        p = i
                        break
                if p == d:
                    print "||"
                    break
                print "->",


if __name__ == '__main__':
    import Data
    import Network

    graph = Network.Topology(20, 5, 2, 0.8, 'BA')
    model = Model(graph)

