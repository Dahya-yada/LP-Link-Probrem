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
        self.Graph = graph
        self.MODEL = grb.Model('LP_MODEL')
        self.X     = 0
        self.M     = 0
        self.H     = 0

        self. non_loop_route = {}

    def make_model(self, s, link_max, link_used, traffic):
        # GUROBIオブジェクト
        self.MODEL = grb.Model('LP_MODEL')
        self.MODEL.setParam('OutputFlag', False)
        # 添字
        D  = self.Graph.site_list
        I  = range(self.Graph.node_num)
        J  = range(self.Graph.node_num)
        # 定数
        #Tsig = self.DATA.signal_vm
        T    = copy.deepcopy(traffic)
        Lmax = copy.deepcopy(link_max)
        Luse = copy.deepcopy(link_used)
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
        
        # for d in D:
        #     for i in I:
        #         for j in J:
        #             self.MODEL.addConstr(X[d,i,j] == X[d,j,i])

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
        #         if i == s or j == d:
                    
        #             continue
        #         self.MODEL.addConstr(grb.quicksum(X[d,i,j] * T for d in D if s != d) + Luse[i,j] <= M,
        #                             'CONST::x.{}.{}*T<=M'.format(i,j))
        for d in D:
            if s == d:
                continue
            self.MODEL.addConstr(grb.quicksum(X[d, i, j] * T + Luse[i, j] for i in I for j in J if Luse[i,j] < Lmax) <= M,
                                 'CONST::X_{}<=M'.format(d))
    
        
        # for i in I:
        #     for j in J:
        #         self.MODEL.addConstr(grb.quicksum(X[d,i,j] for d in D if s != d) <= H, 'CONST::x.{}.{}<=H'.format(i,j))
        for d in D:
            if s == d:
                continue
            self.MODEL.addConstr(grb.quicksum(X[d,i,j] for i in I for j in J) <= H, 'CONST::d.{}<=H'.format(d))
    
    def optimize(self, s, show_route="no"):
        """
        線形計画法による最適化を実行する．
        """
        self.MODEL.optimize()
        self.make_non_loop_route(s)
        if show_route == "yes":
            self.show_route(s)
        print s, "[M]", self.M.x

    def make_non_loop_route(self, s):
        """
        最適化結果からループのないルートを生成します．
        """
        tmp = {d: list() for d in self.Graph.site_list}

        for d in self.Graph.site_list:
            if s == d:
                continue
            loop_idx = []
            appended_idx = []
            p = s
            while(True):
                for n in range(self.Graph.node_num):
                    if self.X[d, p, n].x > 0:
                        tmp[d].append((p, n))
                        loop_idx.append(p)
                        p = int(n)
                        break
                if p in loop_idx:
                    print "*"
                    poped = 0
                    while(True):
                        print "[b_pop]{}: {}".format(d,tmp[d])
                        poped = tmp[d].pop()
                        if poped[0] == p:
                            break
                    print "[pop_end] [orgin]",
                    for ii in range(self.Graph.node_num):
                        for jj in range(self.Graph.node_num):
                            if self.X[d, ii, jj].x >0:
                                print((ii,jj)),
                    print ""
                    for m in range(self.Graph.node_num):
                        if self.X[d, p, m].x > 0 and (p,m) not in appended_idx:
                            print "[append]:", appended_idx
                            tmp[d].append((p,m))
                            appended_idx.append((p,m))
                            p = int(m)
                            break
                    new_loop_idx = []
                    for t in tmp[d]:
                        new_loop_idx.append(t[0])
                    loop_idx = copy.deepcopy(new_loop_idx)
                if p == d:
                    break
        self.non_loop_route = copy.deepcopy(tmp)


    def show_route(self, s):
        """
        構築した経路を表示する．
        """
        print "[SOURCE {}]".format(s)
        for d in self.Graph.site_list:
            if s == d:
                continue
            print "ROUTE: {0:2d} to {1:2d}:".format(s, d),
            for i in range(len(self.non_loop_route[d])):
                print "({0:2d}:{1:3d})".format(self.non_loop_route[d][i][0], self.non_loop_route[d][i][1]),
                if i < len(self.non_loop_route[d])-1:
                    print "->",
                else:
                    print "||"


if __name__ == '__main__':
    import Data
    import Network

    graph = Network.Topology(20, 5, 2, 0.8, 'BA')
    model = Model(graph)

