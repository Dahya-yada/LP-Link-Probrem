# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import os
import csv
import time

import Network
import Model
import Simulator

class Runner(object):
    """
    シミュレーションを実行し，結果をCSVに出力する．
    """
    def __init__(self):
        # シミュレーション条件
        self.node    = 50                # NWノード数
        self.site    = 10                # 拠点数
        self.conn    = 4                 # 1ノードから他のノードへの接続数または1ノードが持つノード数（対応トポロジのみ）
        self.prob    = 0.3               # 他のノードに接続する確率（あるノードが選ばれる確率）（対応トポロジのみ）
        self.t_type  = 'random_regular'  # トポロジ生成アルゴリズム
        self.ln_max  = 100               # 1物理リンクあたりの最大仮想リンク数
        self.lb_max  = 20 * 1024 * 1024  # 1物理リンクあたりの最大仮想リンク帯域
        self.sig_max = 1  * 200000       # 信号量（合計）
        self.sig_div = 20                # 信号量の分割数（信号料/分割数 to 信号料 までシミュレーション）
        self.vm_add  = 100               # VM追加回数
        self.try_num = 10                # シミュレーション回数

        self.simu_dir = 'Simulation_5'    # シミュレーション名
        self.csv_dir  = 'data'           # CSV保存ディレクトリ 
        self.fig_dir  = 'fig'            # 画像保存ディレクトリ

        self.data_std  = []
        self.data_link = []
        self.data_use  = []
    
    def run(self):
        """
        シミュレーション回数だけシミュレーションを実行する．
        """
        try:
            os.makedirs('../{}/{}'.format(self.fig_dir, self.simu_dir))
        except OSError as exc:
            pass
        
        try:
            os.makedirs('../{}/{}'.format(self.csv_dir, self.simu_dir))
        except OSError as exc:
            pass

        time_start = time.time()

        for n in range(self.try_num):
            graph = Network.Topology(self.node, self.site, self.conn,  self.prob, self.t_type)
            model = Model.Model(graph)
            simu  = Simulator.Simulator(graph, model, self.lb_max, self.ln_max, self.sig_max, self.sig_div, self.vm_add)

            fname   = '../{}/{}/{}-割当前.svg'.format(self.fig_dir, self.simu_dir, n + 1)
            fname_a = '../{}/{}/{}-割当後.svg'.format(self.fig_dir, self.simu_dir, n + 1)

            print ''
            print '<{}回目>'.format(n + 1)
            
            graph.generate_images(filename=fname, first=True)
            for i in range(self.vm_add):
                simu.solve(info=True)
            graph.generate_images(filename=fname_a, first=False, costList=simu.x_sig)

            print'[Site]',
            for k in simu.vm_num:
                print '{0:2d}:{1:2d}, '.format(k, simu.vm_num[k]),
            print ''

            self.make_data(simu, n)
        self.make_csv()

        print '[Time of simulation] : {}'.format(time.time() - time_start)
    
    def make_data(self, simu, n):
        """
        CSV書き込み用のデータを生成する．
        """
        if n == 0:
            head_std = ['#',]
            head_use = ['#',]
            for i in range(self.try_num):
                head_std.extend(['std link [{}]'.format(i+1), 'std num [{}]'.format(i+1)])
                head_use.extend(['NUM [{}]'.format(i+1)])
            self.data_std.append(head_std)
            self.data_use.append(head_use)

            for i in range(self.vm_add):
                self.data_std.append([i])
                self.data_use.append([i])

        for i in range(self.vm_add):
            self.data_std[i+1].extend([float(simu.std[i]), float(simu.std_num[i])])
            self.data_use[i+1].extend([int(simu.link_use[i])])
            
        tmp_link_k = simu.x_sig.keys()
        self.data_link.append(tmp_link_k)
        self.data_link.append([simu.x_sig[k] for k in tmp_link_k])
    
    def make_csv(self):
        """
        CSVを生成する．
        """
        csv_std_fname  = '../{}/{}/Std_Dev.csv'.format(self.csv_dir, self.simu_dir)
        csv_link_fname = '../{}/{}/Link.csv'.format(self.csv_dir, self.simu_dir)
        csv_use_fname  = '../{}/{}/Luse.csv'.format(self.csv_dir, self.simu_dir)

        with open(csv_std_fname, 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(self.data_std)
        
        with open(csv_link_fname, 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(self.data_link)
        
        with open(csv_use_fname, 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(self.data_use)

            

if __name__ == '__main__':
    r = Runner()
    r.run()


