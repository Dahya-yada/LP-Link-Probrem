# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import Utils
import gurobipy as grb

class Model(object):
    """
    線形計画モデルオブジェクト
    """

    def __init__(self, graph):
        self.graph = graph
        self.model = grb.Model('LP_MODEL')
        self.X = 0
        self.Y = 0
        self.L = 0
        self.N = 0
        self.route = {}
    
    def make_model(self, s, trf_sig, trf_cp, lb_now, lb_max, ln_now, ln_max, nw_node_now):
        """
        新しい線形計画モデルオブジェクトを生成する．
        """ 
        # Gurobi Object
        self.model = grb.Model('LP_MODEL')

        # Index
        D = [d for d in self.graph.site_list if d != s]
        N = range(self.graph.node_num)

        # Link sets
        ij_set  = [(i,j)   for i in N for j in N if i != j]
        di_set  = [(d,i)   for d in D for i in N if s != d]

        # Variables
        v_x  = {(d,i,j): self.model.addVar(vtype='I', name='x.{}.{}.{}'.format(d,i,j)) for d in self.graph.site_list for i in N for j in N}
        v_l  = self.model.addVar(vtype='I', name='L')
        v_n  = self.model.addVar(vtype='I', name='N')

        # Variable to member
        self.X = v_x
        self.L = v_l
        self.N = v_n

        # 目的関数
        self.model.setObjective((v_l * 100 / lb_max) + (v_n * 200 / ln_max), grb.GRB.MAXIMIZE)

        # 制約: フロー保存
        for d,i in di_set:
            if i == s:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) ==  1)
            if i == d:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) == -1)
            if i != s and i != d:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) ==  0)
        
        # 制約: x,yの範囲
        for d,i,j in v_x:
            self.model.addConstr(v_x[d,i,j] >= 0)
            self.model.addConstr(v_x[d,i,j] <= 1)

        # 制約: リンク数制限
        for i,j in ij_set:
            self.model.addConstr(grb.quicksum(v_x[d,i,j]  for d in D) + ln_now[i,j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j]  for d in D) + ln_now[i,j] <= ln_max)

        # 制約: リンク帯域制限
        for i,j in ij_set:
            self.model.addConstr(grb.quicksum(v_x[d,i,j] * (trf_sig + trf_cp[d]) for d in D) + lb_now[i,j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j] * (trf_sig + trf_cp[d]) for d in D) + lb_now[i,j] <= lb_max)

        # 制約: ノード処理量制限
        for j in N:
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D for i in N) + nw_node_now[j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D for i in N) + nw_node_now[j] <= lb_max)

        # 制約: 各リンクの未使用本数の最小
        for i,j in ij_set:
            if ln_now[i,j] >= ln_max:
                continue
            self.model.addConstr(ln_max - (grb.quicksum(v_x[d,i,j] for d in D) + ln_now[i,j]) >= v_n)

        # 制約: 各リンクの未使用帯域の使用帯域の最小
        for i,j in ij_set:
            if lb_now[i,j] >= lb_max:
                continue
            self.model.addConstr(lb_max - (grb.quicksum(v_x[d,i,j] * (trf_sig + trf_cp[d]) for d in D) + lb_now[i,j]) >= v_l)
    
    def optimize(self, s, trf_sig, trf_cp, lb_now, lb_max, ln_now, ln_max, nw_node_now, info=False):
        """
        モデルを作成し，最適化を実行する．
        もし，infoがTrueなら最適化した経路を表示する．
        """
        self.make_model(s, trf_sig, trf_cp, lb_now, lb_max, ln_now, ln_max, nw_node_now)
        self.model.setParam('OutputFlag', False) # No output Gurobi information about optimization
        self.model.setParam('Therads', 4)
        self.model.optimize()
        # make route
        self.route[s] = self.make_route(s, self.X)

        if info:
            print('[Objective value] {}'.format(self.model.objVal))
            print('<Route>')
            self.show_route(s, self.route)

    def make_route(self, s, x):
        """
        最適化結果から経路を作成する．
        """
        D = self.graph.site_list
        L = self.graph.both_link_list
        N = self.graph.node_num
        allocate = {d: [(i, j) for i, j in L if x[d,i,j].x > 0] for d in D}
        route    = {d: list() for d in self.graph.site_list}

        for d in route:
            passed = []
            tmp = []
            i = s
            while True:
                for j in range(N):
                    if (i,j) in allocate[d]:
                        tmp.append((i,j))
                        passed.append(i)
                        i = j
                        break
                if i == d:
                    break
                if i in passed:
                    poped = ()
                    while True:
                        poped = tmp.pop()
                        del allocate[d][allocate[d].index(poped)]
                        if poped[0] in passed:
                            i = int(poped[0])
                            break
            route[d] = copy.deepcopy(tmp)
        return route

    def show_route(self, s, route):
        """
        求めた経路を表示する．
        """
        print '# FROM site {0:2d}'.format(s)
        for d in route[s]:
            if s == d:
                continue
            print '*  FOR site {0:2d} :'.format(d),
            for i, j in route[s][d]:
                print '({0:2d}, {1:2d}) '.format(i, j),
                if j == d:
                    Utils.StrOut.yellow('END', end='')
                    print ''
                else:
                    Utils.StrOut.yellow('->', end='')
        print ''

if __name__ == '__main__':
    import Network
    graph = Network.Topology(20, 5, 2, 0.8, 'BA')
    model = Model(graph)
    


