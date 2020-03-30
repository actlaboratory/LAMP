# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import logging
import os
import sys
import wx
import re
import ctypes
import pywintypes

import constants
import errorCodes
import globalVars
import menuItemsStore

import view_manager

from logging import getLogger
from simpleDialog import dialog
from .base import *
from simpleDialog import *

import views.mkdir


class MainView(BaseView):
	def __init__(self):
		super().__init__()
		self.identifier="mainView"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800),
			self.app.config.getint(self.identifier,"sizeY",600),
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY")
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		
		# ボタン・音量スライダエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.previousBtn = self.horizontalCreator.button(_("前"), self.events.onButtonClick)
		self.playPauseBtn = self.horizontalCreator.button(_("再生"), self.events.onButtonClick)
		self.nextBtn = self.horizontalCreator.button(_("次"), self.events.onButtonClick)
		self.stopBtn = self.horizontalCreator.button(_("停止"), self.events.onButtonClick)
		self.hFrame.Bind(wx.EVT_BUTTON, self.events.onButtonClick)

		#トラックバーエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.trackBar = self.horizontalCreator.slider(_("トラック"), 1000)
		self.trackBar.Bind(wx.EVT_COMMAND_SCROLL, self.events.onSlider)



		# リストビューエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.playlistView = self.horizontalCreator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_NO_HEADER)
		globalVars.playlist.setListCtrl(self.playlistView)
		view_manager.listViewSetting(self.playlistView)
		self.queueView = self.horizontalCreator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_NO_HEADER)
		globalVars.queue.setListCtrl(self.queueView)
		view_manager.listViewSetting(self.queueView)

		# タイマーの呼び出し
		self.timer = wx.Timer(self.hFrame)
		self.timer.Start(10)
		self.hFrame.Bind(wx.EVT_TIMER, self.events.timerEvent)

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hOperationMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#操作メニューの中身
		self.hOperationInVolumeMenu=wx.Menu()
		self.hOperationMenu.AppendSubMenu(self.hOperationInVolumeMenu, _("音量"))
		self.RegisterMenuCommand(self.hOperationInVolumeMenu, "VOLUME_DEFAULT", _("通常の音量に設定"))
		self.RegisterMenuCommand(self.hOperationInVolumeMenu, "VOLUME_UP", _("音量を上げる"))
		self.RegisterMenuCommand(self.hOperationInVolumeMenu, "VOLUME_DOWN", _("音量を下げる"))

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,"EXAMPLE",_("テストダイアログを閲覧"))

		#メニューバーの生成
		self.hMenuBar=wx.MenuBar()
		self.hMenuBar.Append(self.hOperationMenu,_("操作"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る


		if selected==menuItemsStore.getRef("VOLUME_DEFAULT"):
			globalVars.play.setVolume(100)
		elif selected==menuItemsStore.getRef("VOLUME_UP"):
			globalVars.play.changeVolume(+5)
		elif selected==menuItemsStore.getRef("VOLUME_DOWN"):
			globalVars.play.changeVolume(-5)
		elif selected==menuItemsStore.getRef("FAST_FORWARD"):
			globalVars.play.fastForward()
		elif selected==menuItemsStore.getRef("REWIND"):
			globalVars.play.rewind()
		elif selected==menuItemsStore.getRef("EXAMPLE"):
			d=views.mkdir.Dialog()
			d.Initialize()
			ret=d.Show()
			if ret==wx.ID_CANCEL: return
			dialog(_("入力結果"),str(d.GetValue()))
			return

	def onButtonClick(self, event):
			if event.GetEventObject() == globalVars.app.hMainView.previousBtn:
				globalVars.eventProcess.previousFile()
			if event.GetEventObject() == globalVars.app.hMainView.playPauseBtn:
				globalVars.eventProcess.playButtonControl()
			if event.GetEventObject() == globalVars.app.hMainView.nextBtn:
				globalVars.eventProcess.nextFile()
			if event.GetEventObject() == globalVars.app.hMainView.stopBtn:
				globalVars.eventProcess.stop()

	def onSlider(self, evt):
		if evt.GetEventObject() == globalVars.app.hMainView.trackBar:
			globalVars.eventProcess.trackBarCtrl(evt.GetEventObject())
	
	def timerEvent(self, evt):
		globalVars.eventProcess.refreshView()
		globalVars.eventProcess.fileChange()
