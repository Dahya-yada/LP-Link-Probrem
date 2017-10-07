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
import pylab


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
        self.G_POS    = nx.spring_layout(self.GRAPH)

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
        ネットワークを構成するリンクのリストを生成する．
        :return: 接続ノードの組(タプル)のリスト
        :rtype: tlist
        """
        return self.GRAPH.edges()

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
        リンクをキー，値の初期値をvにしたディクショナリを返す．
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
                        costList=None, maxCost=1000):
        """
        グラフのイメージを生成する．
        :param g: NetworkXグラフオブジェクト
        :param first: 初めてグラフを生成するかどうか
        :param save: イメージを保存するか
        :param filename: 保存する場合のファイル名
        :param cpst_list: リンク帯域のリスト
        """
        # CONFIG
        nSize     = 260
        eColor    = 'red'
        nColor    = 'white'
        linkWidth = 1
        fig_x     = 13
        fig_y     = 8
        fSize     = 11
        fFamily   = 'Nimbus Roman No9 L'

        if g is None:
            g = self.GRAPH

        pylab.figure(figsize=(fig_x, fig_y))
        pylab.xticks([])
        pylab.yticks([])

        if first:
            cMask = [eColor if n in self.site_list else nColor for n in range(self.node_num)]
            nx.draw_networkx_nodes (g, self.G_POS, node_size=nSize, node_color=cMask)
            nx.draw_networkx_edges (g, self.G_POS, width=linkWidth)
            nx.draw_networkx_labels(g, self.G_POS, font_size=fSize, font_family=fFamily)
        else:
            lWidth = [costList[k[0]][k[1]] * 20 /maxCost for k in self.link_list]
            nx.draw_networkx_edges(g, self.G_POS, width=lWidth)

        if save:
            pylab.savefig(filename)
        else:
            pylab.show()


# FOR TEST
if __name__ == "__main__":
    graph = Topology(20, 5, 2, 0.8, 'BA')
    print "拠点："
    print graph.make_site_list()
    print "リンク："
    print graph.make_link_list()
    print "双方向リンク："
    print(graph.make_both_link_list())
    graph.generate_images(first=True, save=False)
