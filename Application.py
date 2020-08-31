# -*- coding: utf-8 -*-
#Application startup file

import win32timezone#ダミー
import m3uManager
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import app as application
import constants
import globalVars

def main():
	app=application.Main()
	globalVars.app=app
	app.initialize()
	app.MainLoop()
	globalVars.play.exit()
	m3uManager.dumpHistory()
	app.config.write()

#global schope
if __name__ == "__main__": main()
