# -*- coding: utf-8 -*-
#Application Main

import AppBase
import event_processor, listManager, lampPipe
import accessible_output2.outputs.auto
import sys
import time
import ConfigManager
import gettext
import logging
import os
import wx
import locale
import win32event
import win32api
import winerror
import datetime
import multiprocessing
import globalVars
import m3uManager
from logging import getLogger, FileHandler, Formatter
from simpleDialog import *
import sleep_timer
from soundPlayer import player, bassController
from soundPlayer.constants import *

import constants
import DefaultSettings
import errorCodes
from views import main

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()
		self.mutex = 0
		multiprocessing.freeze_support() #これがないとマルチプロセスでおかしなことになる


	def initialize(self):
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
		
		self.SetGlobalVars()
		# メインビューを表示
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		m3uloaded = False #条件に基づいてファイルの読み込み
		if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
			if os.path.splitext(sys.argv[1])[1] == ".mp3": globalVars.eventProcess.forcePlay(sys.argv[1])
			elif os.path.splitext(sys.argv[1])[1] == ".m3u" or os.path.splitext(sys.argv[1])[1] == ".m3u8":
				m3uManager.loadM3u(sys.argv[1])
				m3uloaded = True
		startupList = globalVars.app.config.getstring("player", "startupPlaylist", "")
		if startupList != "" and m3uloaded == False: m3uManager.loadM3u(startupList, 1)
		self.hMainView.Show()
		return True

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		if globalVars.app.config.getboolean("player", "fadeOutOnExit", False):
			while globalVars.play.setVolumeByDiff(-2):
				time.sleep(0.07)
		globalVars.play.exit()
		m3uManager.dumpHistory()
		globalVars.app.config.write()
		if self.mutex != 0:
			try: win32event.ReleaseMutex(self.mutex)
			except: pass
			self.mutex = 0
		
		#戻り値は無視される
		return 0

	def SetGlobalVars(self):
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
		if self.mutex != 0:
			try: win32event.ReleaseMutex(self.mutex)
			except: pass
			self.mutex = 0
