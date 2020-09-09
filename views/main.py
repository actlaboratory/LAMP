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
import settings
import m3uManager
import effector
from soundPlayer import player
from soundPlayer.constants import *

import view_manager
from views import mkDialog

from logging import getLogger
from simpleDialog import dialog
from .base import *
from simpleDialog import *

import views.mkdir
import views.mkOpenDialog


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
		self.InstallMenuEvent(Menu(self.identifier, self.events),self.events.OnMenuSelect)
		
		# ボタン・音量スライダエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.previousBtn = self.horizontalCreator.button(_("前"), self.events.onButtonClick)
		self.playPauseBtn = self.horizontalCreator.button(_("再生"), self.events.onButtonClick)
		self.nextBtn = self.horizontalCreator.button(_("次"), self.events.onButtonClick)
		self.stopBtn = self.horizontalCreator.button(_("停止"), self.events.onButtonClick)
		self.repeatLoopBtn = self.horizontalCreator.button(_("ﾘﾋﾟｰﾄ/ﾙｰﾌﾟ"), self.events.onButtonClick)
		self.shuffleBtn = self.horizontalCreator.button(_("ｼｬｯﾌﾙ"), self.events.onButtonClick)
		self.volumeSlider = self.horizontalCreator.slider(_("音量"), 100,
			val=globalVars.app.config.getint("volume","default",default=100, min=0, max=100),
			max=100)
		self.volumeSlider.Bind(wx.EVT_COMMAND_SCROLL, self.events.onSlider)
		self.muteBtn = self.horizontalCreator.button(_("ﾐｭｰﾄ"), self.events.onButtonClick)
		#self.hFrame.Bind(wx.EVT_BUTTON, self.events.onButtonClick)

		#トラックバーエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.trackBar = self.horizontalCreator.slider(_("トラック"), 1000)
		self.trackBar.Bind(wx.EVT_COMMAND_SCROLL, self.events.onSlider)
		self.nowTime = self.horizontalCreator.staticText("0:00:00 / 0:00:00")



		# リストビューエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(1, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL)
		self.playlistView = self.horizontalCreator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_NO_HEADER)
		globalVars.playlist.setListCtrl(self.playlistView)
		view_manager.listViewSetting(self.playlistView, "playlist")
		self.queueView = self.horizontalCreator.ListCtrl(1,wx.EXPAND,style=wx.LC_REPORT|wx.LC_NO_HEADER)
		globalVars.queue.setListCtrl(self.queueView)
		view_manager.listViewSetting(self.queueView, "queue")

		# タイマーの呼び出し
		self.timer = wx.Timer(self.hFrame)
		self.timer.Start(100)
		self.hFrame.Bind(wx.EVT_TIMER, self.events.timerEvent, self.timer)

class Menu(BaseMenu):
	def __init__(self, identifier, event):
		super().__init__(identifier)
		self.event = event
	
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hFunctionMenu = wx.Menu()
		self.hPlaylistMenu=wx.Menu()
		self.hOperationMenu=wx.Menu()
		self.hSettingsMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニューの中身
		self.RegisterMenuCommand(self.hFileMenu,"FILE_OPEN",_("ファイルを開く"))
		self.RegisterMenuCommand(self.hFileMenu,"DIR_OPEN",_("フォルダを開く"))
		self.RegisterMenuCommand(self.hFileMenu,"URL_OPEN",_("URLを開く"))
		self.RegisterMenuCommand(self.hFileMenu,"M3U_OPEN",_("プレイリストを開く"))
		self.RegisterMenuCommand(self.hFileMenu,"NEW_M3U8_SAVE",_("名前を付けてプレイリストを保存"))
		self.RegisterMenuCommand(self.hFileMenu,"M3U8_SAVE",_("プレイリストを上書き保存"))
		self.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), False)
		self.RegisterMenuCommand(self.hFileMenu,"M3U_ADD",_("プレイリストから読み込む"))
		self.RegisterMenuCommand(self.hFileMenu,"M3U_CLOSE",_("プレイリストを閉じる"))
		self.hFileMenu.Enable(menuItemsStore.getRef("M3U_CLOSE"), False)
		self.RegisterMenuCommand(self.hFileMenu,"EXIT",_("終了"))
		#機能メニューの中身
		self.RegisterMenuCommand(self.hFunctionMenu, "SET_SLEEPTIMER", _("スリープタイマーを設定"))
		self.RegisterMenuCommand(self.hFunctionMenu, "SET_EFFECTOR", _("エフェクター"))
		# プレイリストメニューの中身
		self.RegisterMenuCommand(self.hPlaylistMenu,"PLAYLIST_HISTORY_LABEL",_("履歴（20件まで）"))
		self.hPlaylistMenu.Enable(menuItemsStore.getRef("PLAYLIST_HISTORY_LABEL"), False)
		#操作メニューの中身
		self.RegisterMenuCommand(self.hOperationMenu, "PLAY_PAUSE", _("再生 / 一時停止"))
		self.RegisterMenuCommand(self.hOperationMenu, "STOP", _("停止"))
		self.RegisterMenuCommand(self.hOperationMenu, "PREVIOUS_TRACK", _("前へ / 頭出し"))
		self.RegisterMenuCommand(self.hOperationMenu, "NEXT_TRACK", _("次へ"))
		skipRtn = settings.getSkipInterval()
		self.RegisterMenuCommand(self.hOperationMenu, "SKIP", skipRtn[1]+" "+_("進む"))
		self.RegisterMenuCommand(self.hOperationMenu, "REVERSE_SKIP", skipRtn[1]+" "+_("戻る"))
		#スキップ間隔設定
		self.hSetSkipIntervalInOperationMenu=wx.Menu()
		self.hOperationMenu.AppendSubMenu(self.hSetSkipIntervalInOperationMenu, _("スキップ間隔設定"))
		self.RegisterMenuCommand(self.hSetSkipIntervalInOperationMenu, "SKIP_INTERVAL_INCREASE", _("間隔を大きくする"))
		self.RegisterMenuCommand(self.hSetSkipIntervalInOperationMenu, "SKIP_INTERVAL_DECREASE", _("間隔を小さくする"))
		#音量
		self.hVolumeInOperationMenu=wx.Menu()
		self.hOperationMenu.AppendSubMenu(self.hVolumeInOperationMenu, _("音量"))
		self.RegisterMenuCommand(self.hVolumeInOperationMenu, "VOLUME_DEFAULT", _("音量を100%に設定"))
		self.RegisterMenuCommand(self.hVolumeInOperationMenu, "VOLUME_UP", _("音量を上げる"))
		self.RegisterMenuCommand(self.hVolumeInOperationMenu, "VOLUME_DOWN", _("音量を下げる"))
		self.RegisterMenuCommand(self.hVolumeInOperationMenu, "MUTE", _("消音に設定"))
		#リピート・ループ
		self.hRepeatLoopInOperationMenu=wx.Menu()
		self.hOperationMenu.AppendSubMenu(self.hRepeatLoopInOperationMenu, _("リピート・ループ")+"\tCtrl+R")
		self.RegisterRadioMenuCommand(self.hRepeatLoopInOperationMenu, "REPEAT_LOOP_NONE", _("解除する"))
		self.RegisterRadioMenuCommand(self.hRepeatLoopInOperationMenu, "RL_REPEAT", _("リピート"))
		self.RegisterRadioMenuCommand(self.hRepeatLoopInOperationMenu, "RL_LOOP", _("ループ"))
		self.RegisterCheckMenuCommand(self.hOperationMenu, "SHUFFLE", _("シャッフル再生"))
		# 設定メニューの中身
		self.hDeviceChangeInSettingsMenu = wx.Menu()
		self.hSettingsMenu.AppendSubMenu(self.hDeviceChangeInSettingsMenu, _("再生出力先の変更"))

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,"EXAMPLE",_("テストダイアログを閲覧"))

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル"))
		self.hMenuBar.Append(self.hFunctionMenu, _("機能"))
		self.hMenuBar.Append(self.hPlaylistMenu,_("プレイリスト"))
		self.hMenuBar.Append(self.hOperationMenu,_("操作"))
		self.hMenuBar.Append(self.hSettingsMenu,_("設定"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

		# イベント
		target.Bind(wx.EVT_MENU_OPEN, self.event.OnMenuOpen)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る


		if selected==menuItemsStore.getRef("FILE_OPEN"):
			dialog= views.mkOpenDialog.Dialog()
			dialog.Initialize(0) #0=ファイルダイアログ
			rtnCode = dialog.Show()
			if rtnCode == dialog.PLAYLIST:
				globalVars.playlist.addFiles([dialog.GetValue()])
			elif rtnCode == dialog.QUEUE:
				globalVars.queue.addFiles([dialog.GetValue])
			else:
				return
		elif selected==menuItemsStore.getRef("DIR_OPEN"):
			dialog= views.mkOpenDialog.Dialog()
			dialog.Initialize(1) #1=フォルダダイアログ
			rtnCode = dialog.Show()
			if rtnCode == dialog.PLAYLIST:
				globalVars.playlist.addFiles([dialog.GetValue()])
			elif rtnCode == dialog.QUEUE:
				globalVars.queue.addFiles([dialog.GetValue()])
			else:
				return
		elif selected==menuItemsStore.getRef("URL_OPEN"):
			dialog= views.mkOpenDialog.Dialog()
			dialog.Initialize(2) #2=URLダイアログ
			rtnCode = dialog.Show()
			if rtnCode == dialog.PLAYLIST:
				globalVars.playlist.addFiles([dialog.GetValue()])
			elif rtnCode == dialog.QUEUE:
				globalVars.queue.addFiles([dialog.GetValue()])
			else:
				return
		elif selected==menuItemsStore.getRef("M3U_OPEN"):
			m3uManager.loadM3u()
		elif selected==menuItemsStore.getRef("NEW_M3U8_SAVE"):
			m3uManager.saveM3u8()
		elif selected==menuItemsStore.getRef("M3U8_SAVE"):
			m3uManager.saveM3u8(globalVars.playlist.playlistFile)
		elif selected==menuItemsStore.getRef("M3U_ADD"):
			m3uManager.loadM3u(None, m3uManager.ADD)
		elif selected==menuItemsStore.getRef("M3U_CLOSE"):
			m3uManager.closeM3u()
		elif selected == menuItemsStore.getRef("EXIT"):
			self.Exit()
		#機能メニューのイベント
		elif selected == menuItemsStore.getRef("SET_SLEEPTIMER"):
			globalVars.sleepTimer.set()
		elif selected == menuItemsStore.getRef("SET_EFFECTOR"):
			effector.effector()
		# 操作メニューのイベント
		elif selected==menuItemsStore.getRef("PLAY_PAUSE"):
			globalVars.eventProcess.playButtonControl()
		elif selected==menuItemsStore.getRef("STOP"):
			globalVars.eventProcess.stop()
		elif selected==menuItemsStore.getRef("PREVIOUS_TRACK"):
			globalVars.eventProcess.previousBtn()
		elif selected==menuItemsStore.getRef("NEXT_TRACK"):
			globalVars.eventProcess.nextFile()
		elif selected==menuItemsStore.getRef("VOLUME_DEFAULT"):
			globalVars.eventProcess.changeVolume(vol=100)
		elif selected==menuItemsStore.getRef("VOLUME_UP"):
			globalVars.eventProcess.changeVolume(+5)
		elif selected==menuItemsStore.getRef("VOLUME_DOWN"):
			globalVars.eventProcess.changeVolume(-5)
		elif selected==menuItemsStore.getRef("MUTE"):
			globalVars.eventProcess.mute()
		elif selected==menuItemsStore.getRef("FAST_FORWARD"):
			globalVars.play.fastForward()
		elif selected==menuItemsStore.getRef("REWIND"):
			globalVars.play.rewind()
		elif selected==menuItemsStore.getRef("SKIP"):
			globalVars.eventProcess.skip(settings.getSkipInterval()[0])
		elif selected==menuItemsStore.getRef("REVERSE_SKIP"):
			globalVars.eventProcess.skip(settings.getSkipInterval()[0], False)
		elif selected==menuItemsStore.getRef("SKIP_INTERVAL_INCREASE"):
			globalVars.eventProcess.setSkipInterval()
		elif selected==menuItemsStore.getRef("SKIP_INTERVAL_DECREASE"):
			globalVars.eventProcess.setSkipInterval(False)
		elif selected==menuItemsStore.getRef("REPEAT_LOOP"):
			globalVars.eventProcess.repeatLoopCtrl()
		elif selected==menuItemsStore.getRef("REPEAT_LOOP_NONE"):
			globalVars.eventProcess.repeatLoopCtrl(0)
		elif selected==menuItemsStore.getRef("RL_REPEAT"):
			globalVars.eventProcess.repeatLoopCtrl(1)
		elif selected==menuItemsStore.getRef("RL_LOOP"):
			globalVars.eventProcess.repeatLoopCtrl(2)
		elif selected==menuItemsStore.getRef("SHUFFLE"):
			globalVars.eventProcess.shuffleSw()
		elif selected >= constants.DEVICE_LIST_MENU and selected < constants.DEVICE_LIST_MENU + 500:
			if selected == constants.DEVICE_LIST_MENU: globalVars.play.setDevice(PLAYER_DEFAULT_SPEAKER)
			else: globalVars.play.setDevice(selected - constants.DEVICE_LIST_MENU)
		elif selected >= constants.PLAYLIST_HISTORY and selected < constants.PLAYLIST_HISTORY+ 20:
			m3uManager.loadM3u(globalVars.m3uHistory.getList()[selected - constants.PLAYLIST_HISTORY])
		elif selected==menuItemsStore.getRef("EXAMPLE"):
			d = mkDialog.Dialog()
			d.Initialize("テスト", "これはテストです。", ("テ", "ス", "ト"))
			r = d.Show()
			print(r)

	def OnMenuOpen(self, event):
		if event.GetMenu()==self.parent.menu.hDeviceChangeInSettingsMenu:
			menu = self.parent.menu.hDeviceChangeInSettingsMenu
			# 内容クリア
			for i in range(menu.GetMenuItemCount()):
				menu.DestroyItem(menu.FindItemByPosition(0))
			# デバイスリスト追加
			deviceList = player.getDeviceList()
			deviceIndex = 0
			for d in deviceList:
				if deviceIndex == 0: menu.AppendCheckItem(constants.DEVICE_LIST_MENU, _("規定の出力先"))
				elif d != None: menu.AppendCheckItem(constants.DEVICE_LIST_MENU + deviceIndex, d)
				deviceIndex += 1
			# 現在の設定にチェック
			deviceNow = globalVars.play.getConfig(PLAYER_CONFIG_DEVICE)
			if deviceNow == PLAYER_DEFAULT_SPEAKER: menu.Check(constants.DEVICE_LIST_MENU, True)
			elif deviceNow > 0 and deviceNow < len(deviceList) and deviceList[deviceNow] != None: menu.Check(constants.DEVICE_LIST_MENU + deviceNow, True)
		elif event.GetEventObject() == self.parent.menu.hPlaylistMenu:
			menu = self.parent.menu.hPlaylistMenu
			# 履歴部分を削除
			for i in range(menu.GetMenuItemCount() - 1):
				menu.DestroyItem(menu.FindItemByPosition(1))
			# 履歴部分を作成
			index = 0
			for path in globalVars.m3uHistory.getList():
				menu.Insert(1, constants.PLAYLIST_HISTORY + index, path)
				index += 1
	
	def onButtonClick(self, event):
			if event.GetEventObject() == globalVars.app.hMainView.previousBtn:
				globalVars.eventProcess.previousBtn()
			elif event.GetEventObject() == globalVars.app.hMainView.playPauseBtn:
				globalVars.eventProcess.playButtonControl()
			elif event.GetEventObject() == globalVars.app.hMainView.nextBtn:
				globalVars.eventProcess.nextFile()
			elif event.GetEventObject() == globalVars.app.hMainView.stopBtn:
				globalVars.eventProcess.stop()
			elif event.GetEventObject() == globalVars.app.hMainView.repeatLoopBtn:
				globalVars.eventProcess.repeatLoopCtrl()
			elif event.GetEventObject() == globalVars.app.hMainView.shuffleBtn:
				globalVars.eventProcess.shuffleSw()
			elif event.GetEventObject() == globalVars.app.hMainView.muteBtn:
				globalVars.eventProcess.mute()

	def onSlider(self, evt):
		if evt.GetEventObject() == globalVars.app.hMainView.volumeSlider:
			val = globalVars.app.hMainView.volumeSlider.GetValue()
			globalVars.eventProcess.changeVolume(vol=val)
		elif evt.GetEventObject() == globalVars.app.hMainView.trackBar:
			globalVars.eventProcess.trackBarCtrl(evt.GetEventObject())
	
	def timerEvent(self, evt):
		globalVars.eventProcess.refreshView()

	def Exit(self, evt=None):
		globalVars.app.hMainView.timer.Stop()
		globalVars.eventProcess.stop()
		super().Exit()