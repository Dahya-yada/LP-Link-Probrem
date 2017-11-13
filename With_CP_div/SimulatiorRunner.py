# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import csv
import Utils
import Network
import Model
import IdSpace
import Simurator

class Runner(object):
    """
    シミュレーションを実行し，結果をCSVに出力します．
    """
    def __init__(self):
        self.node    = 50                  # NWノード数
        self.site    = 10                  # 拠点数
        self.conn    = 4                   # 1ノードが接続するリンク数
        self.prob    = 0.3                 # 他のノードにリンクが接続する確率(あるリンクの接続ノードに選ばれる確率)(トポロジアルゴリズムが必要とする場合)
        self.t_type  = 'random_regular'    # トポロジ生成アルゴリズム
        self.lb_max  = 1 * 1024 * 1024     # 1物理リンクの最大帯域
        self.ln_max  = 200                 # 1物理リンクの最大仮想リンク数
        self.sig_trf = 4 * 200000 / 3600   # 信号の容量(1拠点あたり)
        self.cpy_trf = 1 * 200000 / 3600   # 複製の容量(1拠点あたり)
        self.t_div   = 5                   # トラヒック分割数
        self.add_n   = 100                 # 最大VM追加数
        self.try_n   = 5                  # シミュレーション回数
        self.id_bit  = 128                 # ID空間の長さ(bit)
        self.id_node = 20                  # 1VMあたりの仮想ノード数

        self.name    = 'Simu_1_div_cp'     # シミュレーション名
        self.csv_dir = 'data'              # CSV保存ディレクトリ
        self.fig_dir = 'fig'               # SVG保存ディレクトリ

        
    def run(self):
        """
        シミュレーションを実行します．
        """
        # Make directory
        dir_data = '../{}/{}'.format(self.csv_dir, self.name)
        dir_fig  = '../{}/{}'.format(self.fig_dir, self.name)
        Utils.DirMaker.make(dir_data)
        Utils.DirMaker.make(dir_fig)
        # Variable declaration
        std_data  = []
        link_data = []
        use_data  = []
        # Measure the time
        timer1 = Utils.Timer()
        # Simulate for try_n times
        for n in range(self.try_n):
            # Generate object
            o_g = Network.Topology(self.node, self.site, self.conn, self.prob, self.t_type)
            o_m = Model.Model(o_g)
            o_i = IdSpace.Space(o_g.site_list, self.id_bit, self.id_node)
            o_s = Simurator.Simulator(o_g, o_m, o_i, self.lb_max, self.ln_max, self.sig_trf, self.cpy_trf, self.add_n)

            Utils.StrOut.blue('\n< {}回目 >'.format(n+1), end='')
            print ''
            timer2 = Utils.Timer()

            o_g.generate_images(filename='{0}/{1:02d}割当前.svg'.format(dir_fig, n + 1), first=True)
            for i in range(self.add_n):
                # self.change_traffic(o_s, self.sig_trf, self.cpy_trf, self.t_div, self.add_n, i)
                o_s.solve(info=True)
            o_g.generate_images(filename='{0}/{1:02d}割当後.svg'.format(dir_fig, n + 1), costList=o_s.x_bw, first=False)

            Utils.StrOut.green('[VM数],', end='')
            for k in o_s.vm_num:
                print '[{0:2d}] {1:2d}, '.format(k, o_s.vm_num[k]),
            Utils.StrOut.yellow('[Time], ', end='')
            print '{:5.2f}\n'.format(timer2.get_time())

            self.make_data(o_s, std_data, link_data, use_data, n)

        Utils.StrOut.yellow('[All Time] {:5.2f}'.format(timer1.get_time()))
        self.output_csv(std_data, link_data, use_data, dir_data)
    
    def change_traffic(self,simu, sig_trf_max, cpy_trf_max, div, add_n, t):
        """
        VM追加回数とvidに合わせてトラヒックを変化させます．
        """
        term     = add_n / div
        sig_unit = sig_trf_max / div
        cpy_unit = cpy_trf_max / div

        if t == 0:
            simu.t_sig = sig_unit
            simu.t_cpy = cpy_unit
            Utils.StrOut.yellow('-> Input ', end='')
            print 'sig = {}, cpy = {}'.format(sig_unit, cpy_unit)
        elif t % term == 0:
            simu.t_sig = sig_unit * ((t / term) + 1)
            simu.t_cpy = cpy_unit * ((t / term) + 1)
            Utils.StrOut.yellow('-> Input ', end='')
            print 'sig = {} cpy = {},'.format(simu.t_sig, simu.t_cpy)

    def make_data(self,simu, std_data, link_data, use_data, n):
        """
        CSV書き込み用のデータを生成します．
        """
        if n == 0:
            head_std = ['# No',]
            head_use = ['# No',]
            for i in range(self.try_n):
                head_std.extend(['STDリンク帯域[{}]'.format(i+1), 'STD仮想リンク数[{}]'.format(i+1)])
                head_use.extend(['使用リンク数[{}]'.format(i+1)])
            std_data.append(head_std)
            use_data.append(head_use)
            for i in range(self.add_n):
                std_data.append([i + 1])
                use_data.append([i + 1])
        
        for i in range(self.add_n):
            std_data[i+1].extend([float(simu.std_bw[i]), float(simu.std_num[i])])
            use_data[i+1].extend([float(simu.use_link[i])])
        
        key_l = simu.x_bw.keys()
        link_data.append(key_l)
        link_data.append([simu.x_bw[k] for k in key_l])

    def output_csv(self, std_data, link_data, use_data, dirpath):
        """
        CSVを生成します．
        """
        f_std   = '{}/std.csv'.format(dirpath)
        f_link  = '{}/link.csv'.format(dirpath)
        f_use   = '{}/use.csv'.format(dirpath)

        with open(f_std, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(std_data)
        with open(f_link, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(link_data)
        with open(f_use, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(use_data)

if __name__ == '__main__':
    runner = Runner()
    runner.run()