# -*- coding: utf-8 -*-
#Application Main

import threading
import sys, os, wx, time, _datetime
import win32event, win32api, winerror
import gettext, locale
import logging
from logging import getLogger, FileHandler, Formatter
import proxyUtil
import AppBase
from simpleDialog import *
from soundPlayer import player, bassController
from soundPlayer.constants import *
import accessible_output2.outputs.auto
import constants, errorCodes
def _import():
	global event_processor, listManager, lampPipe, ConfigManager, globalVars, m3uManager, sleep_timer, DefaultSettings, update, main

	import event_processor, listManager, lampPipe, ConfigManager, globalVars, m3uManager, sleep_timer, DefaultSettings
	import update
	from views import main

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()
		self.mutex = 0

	def initialize(self):
		_import()
		self.log.debug(str(sys.argv))
		# 多重起動処理8
		try: self.mutex = win32event.CreateMutex(None, 1, constants.PIPE_NAME)
		except: pass
		if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
			try: lampPipe.sendPipe()
			except: pass
			self.mutex = 0
			sys.exit()
		else:
			lampPipe.startPipeServer()
		
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		if self.config.getboolean("network", "manual_proxy", False):
			sv = self.config.getstring("network", "proxy_server", "")
			pr = self.config.getint("network", "proxy_port", 8080, 0, 65535)
			self.proxyEnviron.set_environ(sv, pr)
		else: self.proxyEnviron.set_environ()

		self.SetGlobalVars()
		# メインビューを表示
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		m3uloaded = False #条件に基づいてファイルの読み込み
		if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
			if os.path.splitext(sys.argv[1])[1].lower() in globalVars.fileExpansions:
				globalVars.eventProcess.forcePlay(sys.argv[1])
			elif os.path.splitext(sys.argv[1])[1] == ".m3u" or os.path.splitext(sys.argv[1])[1] == ".m3u8":
				m3uManager.loadM3u(sys.argv[1])
				m3uloaded = True
		startupList = globalVars.app.config.getstring("player", "startupPlaylist", "")
		if startupList != "" and m3uloaded == False: m3uManager.loadM3u(startupList, 1)
		return True

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		if globalVars.app.config.getboolean("player", "fadeOutOnExit", False) and globalVars.play.getStatus() == PLAYER_STATUS_PLAYING:
			while globalVars.play.setVolumeByDiff(-2):
				time.sleep(0.07)
		globalVars.play.exit()
		m3uManager.dumpHistory()
		globalVars.app.config.write()
		try: lampPipe.stopPipeServer()
		except: pass
		if self.mutex != 0:
			try: win32event.ReleaseMutex(self.mutex)
			except: pass
			self.mutex = 0

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0

	def SetGlobalVars(self):
		globalVars.update = update.update()
		dl = player.getDeviceList()
		dl[0] = "default"
		dc = globalVars.app.config.getstring("player", "outputDevice", "default", dl)
		if dc == "default": device = PLAYER_DEFAULT_SPEAKER
		elif dc != None: device = dc
		else: device = PLAYER_DEFAULT_SPEAKER
		globalVars.play = player.player(PLAYER_DEFAULT_SPEAKER)
		if device != PLAYER_DEFAULT_SPEAKER: globalVars.play.setDeviceByName(device)
		globalVars.play.setVolume(globalVars.app.config.getint("volume","default",default=100, min=0, max=100))
		globalVars.eventProcess = event_processor.eventProcessor()
		globalVars.sleepTimer = sleep_timer.sleepTimer()
		globalVars.m3uHistory = m3uManager.loadHistory()
		globalVars.listInfo = listManager.listInfo()

	def __del__(self):
		try: lampPipe.stopPipeServer()
		except: pass
		if self.mutex != 0:
			try: win32event.ReleaseMutex(self.mutex)
			except: pass
			self.mutex = 0
