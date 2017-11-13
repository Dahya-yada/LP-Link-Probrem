# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326

"""
CREATE:  2017/02/14
@author: Takahiro Yada
"""
import random as rand
import networkx as nx
import matplotlib.pyplot as plt


class Topology(object):
    """
    ネットワークトポロジ（グラフ）を生成するクラス
    """

    def __init__(self, nodes=10, sites=5, connects=2, probability=0.8, types='BA'):
        """コンストラクタ"""
        self.node_num = nodes
        self.site_num = sites

        self.conn_num = connects
        self.prob     = probability
        self.nw_type  = types

        self.GRAPH    = self.make_graph(nodes, connects, probability, types)
        # self.G_POS    = nx.spring_layout(self.GRAPH,scale=2)
        self.G_POS    = nx.drawing.nx_agraph.graphviz_layout(self.GRAPH, prog='neato')

        self.site_list      = self.make_site_list()
        self.link_list      = self.make_link_list()
        self.both_link_list = self.make_both_link_list()


    def make_graph(self, n, c, p, t):
        """
        NetworkXグラフを生成する．
        :param n: ノード数
        :param e: エッジ数（拠点数）
        :param c: ノードからの接続リンク数
        :param p: 確率
        :param t: トポロジタイプ
        :return: NetworkXグラフオブジェクト
        :rtype: networkx.graph
        """
        if t == 'BA':
            g = nx.barabasi_albert_graph(n, c)
        if t == 'powerlaw_cluster':
            g = nx.powerlaw_cluster_graph(n, c, p)
        if t == 'gnm_random':
            g = nx.gnm_random_graph(n,n*c+1, directed=True)
        if t == 'waxman':
            g = nx.waxman_graph(n,beta=0.3)
        if t == 'random_regular':
            g = nx.random_regular_graph(c,n)
        return g

    def make_site_list(self, n=None):
        """
        ネットワーク内のノードから適当にnだけ拠点を選び，そのリストを返す．
        :param n: 拠点数
        :return: 拠点のリスト
        :rtype: list
        """
        if n is None:
            n = self.site_num
        return rand.sample(range(self.node_num), n)

    def make_link_list(self):
        """
        ネットワークを構成する単方向リンクのリストを生成する．
        :return: 接続ノードの組(タプル)のリスト
        :rtype: tlist
        """
        return list(self.GRAPH.edges())

    def make_both_link_list(self):
        """
        ネットワークを構成する両方向リンクのタプルを生成する．
        :return: 接続ノードの組(タプル)のリスト
        :rtype: list
        """
        l   = self.make_link_list()
        l2  = [(t[1], t[0]) for t in l]
        l.extend(l2)
        return l

    def make_site_dict(self, v=0):
        """
        拠点番号をキー，値の初期値をvにしたディクショナリを返す．
        :param v: 値の初期値
        :return: 拠点のディクショナリ
        :rtype: dict
        """
        key = self.make_site_list()
        return {k: v for k in key}

    def make_link_dict(self, v=0):
        """
        単方向リンクをキー，値の初期値をvにしたディクショナリを返す．
        :param v: 値の初期値
        :return: リンクのディクショナリ
        :rtype: dict
        """
        key = self.make_link_list()
        return {k: v for k in key}

    def make_both_link_dict(self, v=0):
        """
        双方向のリンクをキー，値の初期値をvにしたディクショナリを返す．
        :param v: 値の初期値
        :return: リンクのディクショナリ
        :rtype: dict
        """
        key = self.make_both_link_list()
        return {k: v for k in key}

    def generate_images(self, g=None,
                        first=True, save=True, filename='Toporogy.svg',
                        costList=None,):
        """
        グラフのイメージを生成する．
        :param g: NetworkXグラフオブジェクト
        :param first: 初めてグラフを生成するかどうか
        :param save: イメージを保存するか
        :param filename: 保存する場合のファイル名
        :param cpst_list: リンク帯域のリスト
        """
        # CONFIG
        nSize     = 100
        eColor    = 'red'
        nColor    = 'white'
        linkWidth = 1
        fig_x     = 10
        fig_y     = 7
        fSize     = 11
        fFamily   = 'Inconsolata'

        if g is None:
            g = self.GRAPH

        plt.figure(figsize=(fig_x, fig_y))
        plt.xticks([])
        plt.yticks([])

        cMask = [eColor if n in self.site_list else nColor for n in range(self.node_num)]
        nodes = nx.draw_networkx_nodes (g, self.G_POS, node_size=nSize, node_color=cMask, linewidths=2.0)
        nodes.set_edgecolor('k')
        nx.draw_networkx_edges (g, self.G_POS, width=linkWidth, edge_color='k')
        # nx.draw_networkx_labels(g, self.G_POS, font_size=fSize, font_family=fFamily)

        if first is False:
            max_cost  = max(costList.values())
            lWidth = [5 * costList[i,j] /max_cost for i,j in self.GRAPH.edges()]
            lcolor = [(1.0 * costList[i,j] / max_cost, 0, 1 - 1.0 * costList[i,j] / max_cost) for i,j in self.GRAPH.edges()]
            nx.draw_networkx_edges(g, self.G_POS, width=lWidth, edge_color=lcolor)

        if save:
            plt.savefig(filename)
        else:
            plt.show()


# FOR TEST
if __name__ == "__main__":
    graph = Topology(50, 10, 3, 0.8, 'random_regular')
    print "拠点："
    print graph.make_site_list()
    print "リンク："
    print graph.make_link_list()
    print "双方向リンク："
    print(graph.make_both_link_list())
    graph.generate_images(first=True, save=False)
