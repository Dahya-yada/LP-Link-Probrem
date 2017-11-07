# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy
import gurobipy as grb

class Model(object):
    """
    線形計画モデルオブジェクト
    """
    def __init__(self, graph):
        self.graph = graph
        self.model = grb.Model('LP_MODEL')
        self.X  = 0
        self.Mn = 0
        self.Mb = 0
        self.H  = 0
        self.NN = 0
        self.route = {}

    def make_model(self, s, trf, lb_now, lb_max, ln_now, ln_max, lnn_now):
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
        v_mn = self.model.addVar(vtype='I', name='Mn')
        v_mb = self.model.addVar(vtype='I', name='Mb')
        v_h  = self.model.addVar(vtype='I', name='H')
        v_nn = self.model.addVar(vtype='I', name='N')

        # Variable to member
        self.X  = v_x
        self.Mn = v_mn
        self.Mb = v_mb
        self.NN = v_nn
        self.H  = v_h

        # 目的関数
        self.model.setObjective((v_mb * 200 / lb_max) + (v_mn * 100 / ln_max), grb.GRB.MAXIMIZE)

        # 制約: フロー保存
        for d,i in di_set:
            if i == s:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) ==  1)
            if i == d:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) == -1)
            if i != s and i != d:
                self.model.addConstr(grb.quicksum(v_x[d,i,j] for j in N) - grb.quicksum(v_x[d,j,i] for j in N) ==  0)

        # 制約: xの範囲
        for d,i,j in v_x:
            self.model.addConstr(v_x[d,i,j] >= 0)
            self.model.addConstr(v_x[d,i,j] <= 1)
            
        # 制約: リンク数制限
        for i,j in ij_set:
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D) + ln_now[i,j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D) + ln_now[i,j] <= ln_max)

        # 制約: リンク帯域制限
        for i,j in ij_set:
            self.model.addConstr(grb.quicksum(v_x[d,i,j]       for d in D) + lb_now[i,j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j] * trf for d in D) + lb_now[i,j] <= lb_max)
        
        # 制約: ノード処理量制限
        for j in N:
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D for i in N) + lnn_now[j] >= 0)
            self.model.addConstr(grb.quicksum(v_x[d,i,j] for d in D for i in N) + lnn_now[j] <= lb_max)

        # 制約: 各リンクの未使用本数の最小
        for i,j in ij_set:
            if ln_now[i,j] >= ln_max:
                continue
            self.model.addConstr(ln_max - (grb.quicksum(v_x[d,i,j] for d in D) + ln_now[i,j]) >= v_mn)
        
        # 制約: 各リンクの未使用帯域の使用帯域の最小
        for i,j in ij_set:
            if lb_now[i,j] >= lb_max:
                continue
            self.model.addConstr(lb_max - (grb.quicksum(v_x[d,i,j] * trf for d in D) + lb_now[i,j]) >= v_mb)

        # 制約: 各NWノードの未使用容量の最小
        # for j in N:
        #     self.model.addConstr(lb_max / 10 - (grb.quicksum(v_x[d,i,j] * trf  for d in D for i in N) + lnn_now[j]) >= v_nn, 'const:M_band')
        # self.model.addConstr(
        #     grb.quicksum(lb_max - grb.quicksum(grb.quicksum(v_x[d,i,n] for d in D) + lnn_now[n] for i in N) for n in N) >= v_nn,
        #     'Const:NN'
        # )


        # 制約
        # for d in D:
        #     self.model.addConstr(grb.quicksum( grb.quicksum(lb_now[k,j] for k in N) * v_x[d,i,j] for i,j in ij_set) <= v_h, 'const_H')
        
        # # 制約: ホップ数の最大
        # for d in D:
        #     self.model.addConstr(grb.quicksum(v_x[d,i,j] for i,j in ij_set) >= v_h, 'const:H')

    def optimize(self, s, trf, lb_now, lb_max, ln_now, ln_max, nn_now, info=False):
        """
        モデルを作成し，最適化を実行する．
        もし，infoがTrueなら最適化した経路を表示する．
        """

        self.make_model(s, trf, lb_now, lb_max, ln_now, ln_max, nn_now)

        self.model.setParam('OutputFlag', False)

        self.model.optimize()
        self.make_route(s)

        if info:
            print '[M_num] value: {}  [M_band] value: {}'.format(self.Mn.x, self.Mb.x)
            self.show_route(s)
        
    def make_route(self, s):
        """
        最適化結果から経路を作成する．
        """
        D = self.graph.site_list
        L = self.graph.both_link_list
        N = self.graph.node_num
        allocate = {d: [(i, j) for i, j in L if self.X[d,i,j].x > 0] for d in D}
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
        self.route[s] = copy.deepcopy(route)

    def show_route(self, s):
        """
        求めた経路を表示する．
        """
        print '# FROM site {0:2d}'.format(s)
        for d in self.route[s]:
            if s == d:
                continue
            print '*  FOR site {0:2d} :'.format(d),
            for l in self.route[s][d]:
                print '({0:2d}, {1:2d})'.format(l[0], l[1]),
                if l[1] == d:
                    print ''
                else:
                    print '->',
        print ''


if __name__ == '__main__':
    import Network
    graph = Network.Topology(20, 5, 2, 0.8, 'BA')
    model = Model(graph)