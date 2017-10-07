# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

class Data(object):
    """
    線形計画法に使用するデータ
    """
    def __init__(self, graph, bandwidth_max, signal_traffic_max, signal_division):
        self.graph = graph
        self.bandwidth_max      = bandwidth_max
        self.signal_traffic_max = signal_traffic_max
        self.signal_division    = signal_division
        self.signal_unit        = signal_traffic_max / signal_division
        self.signal_now         = self.signal_unit

        self.links_x     = self.graph.make_link_list()
        self.sites_x     = self.make_site_link_dic()
        self.sites_x_tmp = self.make_site_link_dic()
        self.solve_x     = self.make_link_matrix() 

    def make_link_matrix(self):
        """
        リンクのマトリックスを生成する．
        """
        dic = {(i, j): self.bandwidth_max for i in range(self.graph.node_num) for j in range(self.graph.node_num)}
        for index in self.graph.make_both_link_list():
            dic[index] = 0
        
        return dic

    def make_site_link_dic(self):
        """
        拠点ごとのリンク帯域のディクショナリを生成する．
        """
        dic = {k: self.make_link_matrix() for k in self.graph.site_list}
        return dic

# FOR TEST

if __name__ == '__main__':
    import Network as nw

    Graph = nw.Topology()
    Data  = Data(Graph, 10000, 1000, 10)