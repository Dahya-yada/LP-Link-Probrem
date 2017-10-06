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

    def __init__(self, nodes=10, edges=5, connect=2, probability=0.8, types='BA'):
        """コンストラクタ"""
        self.ノード数 = nodes
        self.拠点数   = edges
        self.接続数   = connect
        self.確率     = probability
        self.タイプ   = types

        self.グラフ = self.generate_graph(nodes, connect, probability, types)
        self.G_POS = nx.spring_layout(self.グラフ)
        self.拠点リスト = self.list_edges()
        self.リンクリスト = self.list_links()

    def generate_graph(self, n, c, p, t):
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

    def iter_nodes(self, n=None):
        """
        ネットワークを構成するノードのイテレータを生成する．
        :param n: ノード数
        :return: ノード番号
        :rtype: int
        """
        if n is None:
            n = self.ノード数

        for i in range(n):
            yield i

    def list_links(self, g=None):
        """
        ネットワークを構成するリンクのイテレータを生成する．
        :param g: NetworkXグラフオブジェクト
        :return: 接続ノードのタプル
        :rtype: tuple
        """
        if g is None:
            g = self.グラフ
        return g.edges()


    def list_both_links(self):
        """
        ネットワークを構成する両方向リンクのイテレータを生成する．
        :param g: NetworkXグラフオブジェクト
        :return: 接続ノードのタプル
        :rtype: tuple
        """
        l = []
        for n in self.グラフ.edges():
            l.append(n)
            l.append((n[1],n[0]))
        return l

    def list_edges(self, n=None, e=None):
        """
        ネットワーク内のノードから適当にeだけエッジノード（拠点）を選び，そのリストを返す．
        :param e: エッジ数
        :return: エッジノードのリスト
        :rtype: list
        """
        if n is None:
            n = self.ノード数
        if e is None:
            e = self.拠点数

        e_node = rand.sample(list(self.iter_nodes(n)), e)
        return e_node

    def iter_edges(self, e=None):
        """
        ネットワーク内のノードから選出されたエッジノード（拠点）のイテレータを生成する．
        :param e: エッジノードのリスト
        :return: 拠点番号
        :rtype: int
        """
        if e is None:
            e = self.拠点リスト
        for i in e:
            yield e
        

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
        fFamily   = 'Kozuka Gothic Pr6N'

        if g is None:
            g = self.グラフ

        pylab.figure(figsize=(fig_x, fig_y))
        pylab.xticks([])
        pylab.yticks([])

        if first:
            cMask = [eColor if n in self.拠点リスト else nColor for n in self.iter_nodes()]
            nx.draw_networkx_nodes (g, self.G_POS, node_size=nSize, node_color=cMask)
            nx.draw_networkx_edges (g, self.G_POS, width=linkWidth)
            nx.draw_networkx_labels(g, self.G_POS, font_size=fSize, font_family=fFamily)
        else:
            lWidth = [costList[k[0]][k[1]] * 20 /maxCost for k in self.iter_links()]
            nx.draw_networkx_edges(g, self.G_POS, width=lWidth)

        if save:
            pylab.savefig(filename)
        else:
            pylab.show()


# FOR TEST
if __name__ == "__main__":
    graph = Topology(20, 5, 2, 0.8, 'BA')
    #print(list(graph.iter_nodes()))
    #print(graph.list_edges())
    print(graph.list_links())
    graph.generate_images(first=True, save=False)
