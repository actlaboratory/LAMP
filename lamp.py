# -*- coding: utf-8 -*-
#Application startup file

import sys, os
#カレントディレクトリを設定
if hasattr(sys,"frozen"): os.chdir(os.path.dirname(sys.executable))
else: os.chdir(os.path.abspath(os.path.dirname(__file__)))

#エラーの出力
import traceback
def exchandler(type, exc, tb):
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	f=open("errorLog.txt", "a")
	f.writelines(msg)
	f.close()

sys.excepthook=exchandler

import multiprocessing
multiprocessing.freeze_support() #これがないとマルチプロセスでおかしなことになる

import win32timezone#ダミー
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.getcwd())
	sys.path.append(os.getcwd())


import simpleDialog
simpleDialog.dialog("debug", str(os.getcwd()) + "\n" + "\n".join(sys.argv))

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
