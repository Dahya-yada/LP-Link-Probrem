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
        self.bandwidth_max = bandwidth_max
        self.signal_traffic_max=signal_traffic_max
        self.signal_division=signal_division
    
    def make_link_array(self):
         


if __name__ == '__main__':
    import Network = nw

    Graph = nw.Toporogy();
    Data  = Data(Graph, 10000, 1000, 10)