# -*- coding: utf-8 -*-
# なんかテキスト処理とか便利なやつを呼び出しやすいようにするクラス群

import colorama as col
import time

class StrOut(object):
    """
    色付きで文字列を出力するメソッド群
    """

    @staticmethod
    def blue(string, newline=True):
        """
        色: Blueで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is blue
        """
        if newline:
            print col.Fore.BLUE + string + col.Fore.RESET
        else
            print col.Fore.BLUE + string + col.Fore.RESET,
    
    @staticmethod
    def green(string):
        """
        色: Greenで標準出力に文字列stringを出力します．

        >>> StrOut.green('String')
        String # Fore color is green
        """
        if newline:
            print col.Fore.GREEN + string + col.Fore.RESET
        else
            print col.Fore.GREEN + string + col.Fore.RESET,
    
    @staticmethod
    def yellow(string):
        """
        色: Yellowで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is yellow
        """
        if newline:
            print col.Fore.YELLOW + string + col.Fore.RESET
        else
            print col.Fore.YELLOW + string + col.Fore.RESET,
    
    @staticmethod
    def magenta(string):
        """
        色: Magentaで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is magenta
        """
        if newline:
            print col.Fore.MAGENTA + string + col.Fore.RESET
        else
            print col.Fore.MAGENTA + string + col.Fore.RESET,

    staticmethod
    def cyan(string):
        """
        色: Cyanで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is cyan
        """
        if newline:
            print col.Fore.CYAN + string + col.Fore.RESET
        else
            print col.Fore.CYAN + string + col.Fore.RESET,

    staticmethod
    def red(string):
        """
        色: Redで標準出力に文字列stringを出力します．

        >>> StrOut.blue('String')
        String # Fore color is red
        """
        if newline:
            print col.Fore.RED + string + col.Fore.RESET
        else
            print col.Fore.RED + string + col.Fore.RESET,
    

class Timer(object):
    """
    時間を計測する関数群
    """
    def __init__(self)
        self.start_time = 0
        self.finish_time = 0
        self.start()
    
    def start(self):
        self.start_time = time.time()
    
    def finish(self):
        self.finish_time = time.time()
        return self.finish_time - self.start_time

    def get_time(self):
        self.finish_time = time.time()
        return self.finish_time - self.start_time

