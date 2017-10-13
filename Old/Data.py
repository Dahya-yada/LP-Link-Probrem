# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import copy

class Data(object):
    """
    線形計画法に使用するデータ
    """
    def __init__(self, o_graph, bandwidth_max, signal_traffic_max, signal_division, vm_add_num):
        self.graph   = o_graph
        self.try_num = vm_add_num
        self.try_now = 0

        self.bandwidth_max = bandwidth_max
        self.signal_max    = signal_traffic_max
        self.signal_div    = signal_division
        self.signal_unit   = signal_traffic_max / signal_division
        self.signal_lb     = self.signal_unit
        self.signal_vm     = 0

        self.link_x = self.graph.make_link_list()
        self.x_sig  = self.graph.make_link_dict()
        self.x_cpy  = self.graph.make_link_dict()

        # self.sites_list  = copy.deepcopy(self.graph.site_list)
        self.vm_num      = {k: 0 for k in self.graph.site_list}

        self.std_dev     = {k + 1: 0 for k in range(vm_add_num)}

    def make_link_matrix(self):
        """
        リンクのマトリックスを生成する．
        """
        dic = {(i, j): self.bandwidth_max for i in range(self.graph.node_num) for j in range(self.graph.node_num)}
        for index in self.graph.make_both_link_list():
            dic[index] = 0
        
        return dic
    def make_num_sites_link_dict(self):
        """
        VM追加回数，拠点，単方向リンクを添え字に持つディクショナリを返す．
        """
        t_num  = range(self.try_num)
        s_list = self.graph.site_list
        return {p: {q: {r: 0 for r in self.graph.link_list} for q in t_num} for p in s_list}

    def make_site_link_dict (self):
        """
        拠点ごとの単方向リンク帯域のディクショナリを生成する．
        """
        dic = {k: self.graph.make_link_dict() for k in self.graph.site_list}
        return dic

# FOR TEST

if __name__ == '__main__':
    import Network as nw

    graph = nw.Topology()
    data  = Data(graph, 10000, 1000, 10, 100)