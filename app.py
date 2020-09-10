# -*- coding: utf-8 -*-
#Application Main

import AppBase
import lists, event_processor, data_dict, lampPipe
import accessible_output2.outputs.auto
import sys
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
import globalVars
import m3uManager
import data_dict
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

	def initialize(self):
		# 多重起動処理8
		self.mutex = win32event.CreateMutex(None, 1, constants.PIPE_NAME)
		if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
			lampPipe.sendPipe()
			self.mutex = 0
			exit()
		else:
			lampPipe.startPipeServer()
		
		self.SetGlobalVars()
		# メインビューを表示
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
			if os.path.splitext(sys.argv[1])[1] == ".mp3": globalVars.eventProcess.forcePlay(sys.argv[1])
			elif os.path.splitext(sys.argv[1])[1] == ".m3u" or os.path.splitext(sys.argv[1])[1] == ".m3u8":
				m3uManager.loadM3u(sys.argv[1])
		self.hMainView.Show()
		return True

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。


		#戻り値は無視される
		return 0

	def SetGlobalVars(self):
		globalVars.play = player.player(PLAYER_DEFAULT_SPEAKER)
		globalVars.play.setVolume(globalVars.app.config.getint("volume","default",default=100, min=0, max=100))
		globalVars.playlist = lists.playlist()
		globalVars.queue = lists.queue()
		globalVars.eventProcess = event_processor.eventProcessor()
		globalVars.dataDict = data_dict.dataDict()
		globalVars.sleepTimer = sleep_timer.sleepTimer()
		globalVars.m3uHistory = m3uManager.loadHistory()

	def __del__(self):
		if self.mutex != 0:
			win32event.ReleaseMutex(self.mutex)
			self.mutex = 0