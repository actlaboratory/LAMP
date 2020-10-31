# -*- coding: utf-8 -*-
#Application startup file

import multiprocessing
import win32timezone#ダミー
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Python3.8対応
#dllやモジュールをカレントディレクトリから読み込むように設定
import sys

multiprocessing.freeze_support() #これがないとマルチプロセスでおかしなことになる

if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app as application
import constants
import globalVars
import m3uManager

def main():
	app=application.Main()
	globalVars.app=app
	app.initialize()
	app.MainLoop()


#global schope
if __name__ == "__main__": main()
