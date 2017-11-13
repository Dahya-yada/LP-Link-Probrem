# -*- coding: utf-8 -*-
# なんかテキスト処理とか便利なやつを呼び出しやすいようにするクラス群

from __future__ import print_function
import time
import os
import colorama as col

class StrOut(object):
    """
    色付きで文字列を出力するメソッド群
    """

    @staticmethod
    def blue(string, end='\n'):
        """
        色: Blueで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is blue
        """
        col.init()
        print(col.Fore.BLUE + string + col.Fore.RESET, end=end)
    
    @staticmethod
    def green(string, end='\n'):
        """
        色: Greenで標準出力に文字列stringを出力します．

        >>> StrOut.green('String')
        String # Fore color is green
        """
        col.init()
        print(col.Fore.GREEN + string + col.Fore.RESET, end=end)
    
    @staticmethod
    def yellow(string, end='\n'):
        """
        色: Yellowで標準出力に文字列stringを出力します．

        >>> StrOut.yellow('String')
        String # Fore color is yellow
        """
        col.init()
        print(col.Fore.YELLOW + string + col.Fore.RESET, end=end)
    
    @staticmethod
    def magenta(string, end='\n'):
        """
        色: Magentaで標準出力に文字列stringを出力します．

        >>> StrOut.magenta('String')
        String # Fore color is magenta
        """
        col.init()
        print(col.Fore.MAGENTA + string + col.Fore.RESET, end=end)

    @staticmethod
    def cyan(string, end='\n'):
        """
        色: Cyanで標準出力に文字列stringを出力します．

        >>> StrOut.cyan('String')
        String # Fore color is cyan
        """
        col.init()
        print(col.Fore.CYAN + string + col.Fore.RESET, end=end)

    @staticmethod
    def red(string, end='\n'):
        """
        色: Redで標準出力に文字列stringを出力します．

        >>> StrOut.red('String')
        String # Fore color is red
        """
        col.init()
        print(col.Fore.RED + string + col.Fore.RESET, end=end)
    

class Timer(object):
    """
    時間を計測する関数群です．
    このクラスをインスタンス化すると時間の計測を開始します．
    """
    def __init__(self):
        self.start_time = 0
        self.finish_time = 0
        self.start()
    
    def start(self):
        """
        時間の計測を開始します．
        このクラスのインスタンス変数start_timeに開始時刻を格納します．
        """
        self.start_time = time.time()
    
    def finish(self):
        """
        時間の計測を終了すします．計測開始から終了までの時間を取得します．
        このクラスのインスタンス変数finish_timeに終了時刻を格納します
        """
        self.finish_time = time.time()
        return self.finish_time - self.start_time

    def get_time(self):
        """
        計測開始からの経過時間を取得します．
        このクラスのインスタンス変数finish_timeに時刻を格納しません．
        """
        return time.time() - self.start_time


class DirMaker(object):
    """
    ディレクトリを作成します．
    """
    @staticmethod
    def make(dirpath):
        """
        dirpathに指定されたディレクトリを作成します．
        dirpathになるように中間のディレクトリも作成します．
        """
        if os.path.exists(dirpath):
            return
        else:
            os.makedirs(dirpath)