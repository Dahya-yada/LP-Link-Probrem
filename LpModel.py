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
    def __init__(self, data):
        self.DATA  = data
        self.MODEL = grb.Model('LP_MODEL')
        self.X     = 0

    def make_model(self, s):
        # GUROBIオブジェクト
        self.MODEL = grb.Model('LP_MODEL')
        self.MODEL.setParam('OutputFlag', False)
        # 添字
        D  = self.DATA.graph.site_list
        I  = range(self.DATA.graph.node_num)
        J  = range(self.DATA.graph.node_num)
        # 定数
        Tsig = self.DATA.signal_site
        Lmax = self.DATA.bandwidth_max
        Luse = self.DATA.solve_x
        # 変数
        X = {(d, i, j): self.MODEL.addVar(vtype='B', name='x.{}.{}.{}'.format(d,i,j)) for j in J for i in I for d in D}
        M = self.MODEL.addVar(vtype='I', name='M')

        self.X = X

        # モデルのアップデート
        self.MODEL.update()

        # 目的関数
        self.MODEL.setObjective(M, grb.GRB.MINIMIZE)

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
                    self.MODEL.addConstr(X[d,i,j] * Tsig >= 0, 
                                         'CONST::traff_x.{}.{}.{}>=0'.format(d,i,j))
                    self.MODEL.addConstr(X[d,i,j] * Tsig + Luse[i,j] <= Lmax, 
                                         'CONST::traff_x.{}.{}.{}<=MAX'.format(d,i,j))

        for i in I:
            for j in J:
                if Luse[i,j] >= Lmax:
                    continue
                # self.MODEL.addConstr(grb.quicksum(X[d,i,j] for d in D if s != d) + Luse[i,j] <= M, 
                #                      'CONST::x.{}.{} <= M'.format(i,j))
                self.MODEL.addConstr(grb.quicksum(X[d,i,j] * Tsig for d in D if s != d) + Luse[i,j] <= M,
                                    'CONST::x.{}.{} <= M'.format(i,j))

if __name__ == '__main__':
    import Data
    import Network

    graph = Network.Topology(20, 5, 2, 0.8, 'BA')
    data  = Data.Data(graph, 10000, 1000,10)
    model = Model(data)