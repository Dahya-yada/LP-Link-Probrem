# -*- coding: utf-8 -*-

# IGNORE RULES OF PYLINT !
# pylint: disable=C0103
# pylint: disable=C0326
# pylint: disable=C0301

import matplotlib.pyplot as plt

class Space(object):
    """
    領域二等分法によるID空間を表します．
    """
    def __init__(self, sites, bit_length=128, node_num=20):
        self.bit_len   = bit_length
        self.length    = 2 ** bit_length
        self.space_max = self.length - 1

        self.sites    = sites
        self.node_num = node_num

        self.locate      = {}
        self.lap         = 1
        self.step        = 0
        self.is_interm   = False
        self.interm_node = []

        self.vm_id     = {s:0 for s in self.sites}
        self.vm_num_id = []
    
    def add_vm(self, site='INTERM'):
        """
        VM追加に伴う仮想ノード追加を行う．
        """
        if self.is_interm:
            try:
                raise IsIntermNodeError('拠点が未確定の仮想ノードがID空間上に配置されています．そのノードの拠点を確定してください．')
            except IsIntermNodeError as e:
                print e
        
        if site == 'INTERM':
            self.is_interm = True
            vm_id = 'Unknown'
        else:
            vm_id = self.vm_id[site]
        
        i = 0
        while i < self.node_num: 
            if 2 ** self.lap == self.step:
                self.lap += 1
                self.step = 0
            
            target_loc = self.length * self.step / (2 ** self.lap)

            if target_loc not in self.locate:
                self.locate[target_loc] = [site, vm_id, i+1]
                if site == 'INTERM':
                    self.interm_node.append(target_loc)
                i += 1

            self.step += 1

        self.vm_num_id.append([site,vm_id])
        if site != 'INTERM':
            self.vm_id[site] += 1
    
    def decide_interm_site(self, site):
        """
        VM追加拠点が不明なノードの所属拠点を決定する．
        """
        for k in self.interm_node:
            self.locate[k][0] = int(site)
            self.locate[k][1] = int(self.vm_id[site])
        
        pop_vm_num_id = self.vm_num_id.pop()
        pop_vm_num_id[0] = int(site)
        pop_vm_num_id[1] = int(self.vm_id[site])
        self.vm_num_id.append(pop_vm_num_id)

        self.vm_id[site] += 1
        self.interm_node = []
        self.is_interm = False
    
    def get_right_node(self, site='INTERM',vm='Unknown'):
        """
        あるVMの仮想ノードの右隣の仮想ノード数を返す．
        """
        s_list = [v for v in self.locate if self.locate[v][0] == site and self.locate[v][1] == vm]
        s_list.sort()
        a_list = list(self.locate.keys())
        a_list.sort()

        site_list = {s: 0 for s in self.sites}
        site_list["INTERM"] = 0
        for v in s_list:
            idx = a_list.index(v) + 1
            if len(a_list) <= idx:
                site_list[self.locate[0][0]] += 1
            else:
                site_list[self.locate[a_list[idx]][0]] += 1

        return site_list

    def get_right_node_by_id(self, id_num):
        """
        あるVMの仮想ノードの右隣の仮想ノード数を返す．
        VM追加番号で検索する．
        """
        if id_num is None:
            return self.get_right_node()
        else:
            s, v = self.vm_num_id[id_num]
            return self.get_right_node(s, v)

    def show_image(self):
        """
        ID空間と仮想ノード配置図を表示します．
        """
        value = []
        label = []
        loc   = sorted(self.locate.keys())
        dif_v = 0
        for k in loc:
            value.append(1.0 * (k - dif_v) / self.length)
            ns, nv, nn = self.locate[k]
            label.append('S:{}, V:{}, N:{}'.format(ns,nv,nn))
            dif_v = k
        value.append(1 - 1.0 * (dif_v) / self.length)
        label.append("")

        plt.figure(figsize=(10,10))
        plt.pie(x=value, labels=label, colors="w",wedgeprops={'edgecolor':'black'}, counterclock=False, startangle=90)
        plt.show()


class IsIntermNodeError(Exception):
    """
    拠点が不明な仮想ノードがID空間上に存在するときのエラー
    """
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return 'Exist interm nodes: {}'.format(self.value)


if __name__ == '__main__':
    space = Space([1,2,3], 128, 20)
    space.add_vm()
    # space.add_vm(3)
    # space.add_vm(1)
    # space.add_vm(2)
    # space.add_vm(3)
    # space.add_vm()
    # space.decide_interm_site(1)
    print space.get_right_node()
    print space.vm_num_id
    space.show_image()
