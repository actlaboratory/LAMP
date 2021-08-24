# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2020-2021 Hiroki Fujii <hfujii@hisystron.com>

from views import fileAssocDialog
from views import filterSettingDialog
from views import globalKeyConfig
from views import lampViewObject
from views import netFileManager
from views import notificationText
from views import setting_dialog
from views import versionDialog

import ctypes
import logging
import os
import pywintypes
import re
import subprocess
import sys
import time
import wx

import constants
import errorCodes
import globalVars
import netRemote
import hotkeyHandler
import menuItemsStore
import menuItemsDic
import settings
import ConfigManager
import m3uManager
import effector
import startupListSetter
import listManager
import update

from soundPlayer import player
from soundPlayer.constants import *

import view_manager
import sendToManager

from logging import getLogger
from simpleDialog import dialog
from .base import *
from simpleDialog import *

import views.mkOpenDialog


class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
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
		
		# 矢印キーUpを握りつぶしてショートカットキーの重複を回避
		def stopArrowPropagation(evt):
			if evt.GetKeyCode() in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT): evt.StopPropagation()
			else: evt.Skip()
		

		#上余白
		self.creator.AddSpace(15)

		# ボタン・音量スライダエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL,style=wx.LEFT | wx.RIGHT | wx.EXPAND,space=20,margin=65)
		self.previousBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		view_manager.setBitmapButton(self.previousBtn, self.hPanel, wx.Bitmap("./resources/back.dat", wx.BITMAP_TYPE_GIF), _("前へ"))
		self.playPauseBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		view_manager.setBitmapButton(self.playPauseBtn, self.hPanel, wx.Bitmap("./resources/play.dat", wx.BITMAP_TYPE_GIF), _("再生"))
		self.nextBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		view_manager.setBitmapButton(self.nextBtn, self.hPanel, wx.Bitmap("./resources/next.dat", wx.BITMAP_TYPE_GIF), _("次へ"))
		self.stopBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		view_manager.setBitmapButton(self.stopBtn, self.hPanel, wx.Bitmap("./resources/stop.dat", wx.BITMAP_TYPE_GIF), _("停止"))
		self.repeatLoopBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		if globalVars.eventProcess.repeatLoopFlag == 2:
			view_manager.setBitmapButton(self.repeatLoopBtn, self.hPanel, wx.Bitmap("./resources/loop_on.dat", wx.BITMAP_TYPE_GIF), _("リピートとループを解除する"))
		elif globalVars.eventProcess.repeatLoopFlag == 1:
			view_manager.setBitmapButton(self.repeatLoopBtn, self.hPanel, wx.Bitmap("./resources/repeat_on.dat", wx.BITMAP_TYPE_GIF), _("ループに切り替える"))
		else: view_manager.setBitmapButton(self.repeatLoopBtn, self.hPanel, wx.Bitmap("./resources/repeatLoop.dat", wx.BITMAP_TYPE_GIF), _("リピートに切り替える"))
		
		self.shuffleBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, enableTabFocus=False)
		if globalVars.eventProcess.shuffleCtrl == None:
			view_manager.setBitmapButton(self.shuffleBtn, self.hPanel, wx.Bitmap("./resources/shuffle_off.dat", wx.BITMAP_TYPE_GIF), _("シャッフルをオンにする"))
		else: view_manager.setBitmapButton(self.shuffleBtn, self.hPanel, wx.Bitmap("./resources/shuffle_on.dat", wx.BITMAP_TYPE_GIF), _("シャッフルをオフにする"))
		self.horizontalCreator.GetSizer().AddStretchSpacer(1)
		self.muteBtn = self.horizontalCreator.button("", self.events.onButtonClick, style=wx.BU_NOTEXT|wx.BU_EXACTFIT|wx.BORDER_NONE, sizerFlag=wx.ALL|wx.ALIGN_CENTER, enableTabFocus=False)
		if globalVars.app.config.getstring("view","colorMode","white",("white","dark")) == "white":
			view_manager.setBitmapButton(self.muteBtn, self.hPanel, wx.Bitmap("./resources/volume.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオンにする"))
		else: view_manager.setBitmapButton(self.muteBtn, self.hPanel, wx.Bitmap("./resources/volume_bk.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオンにする"))
		self.volumeSlider, dummy = self.horizontalCreator.clearSlider(_("音量"), 0, 100, None,
			globalVars.app.config.getint("volume","default",default=100, min=0, max=100), x=150, sizerFlag=wx.ALIGN_CENTER, textLayout=None)
		self.volumeSlider.setScrollCallBack(self.events.onVolumeSlider)
		self.volumeSlider.Bind(wx.EVT_KEY_UP, stopArrowPropagation)
		self.volumeSlider.SetThumbLength(25)
		self.volumeSlider.setToolTip(self.val2vol)
		#self.hFrame.Bind(wx.EVT_BUTTON, self.events.onButtonClick)

		self.creator.AddSpace(10)

		# 曲情報表示
		infoCreator = views.ViewCreator.ViewCreator(self.viewMode, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL,0, style=wx.EXPAND | wx.LEFT | wx.RIGHT, margin=60)
		lb = infoCreator.staticText("♪")
		f = lb.GetFont()
		f.SetPointSize(f.GetPointSize() * (5/3))
		lb.SetFont(f)
		infoRight = views.ViewCreator.ViewCreator(self.viewMode, infoCreator.GetPanel(), infoCreator.GetSizer(), wx.VERTICAL,0, style=wx.EXPAND | wx.LEFT, margin=5, proportion=1)
		self.viewTitle = infoRight.staticText("")
		self.viewTagInfo = infoRight.staticText("")
		f = self.viewTagInfo.GetFont()
		f.SetPointSize(f.GetPointSize() * (2/3))
		self.viewTagInfo.SetFont(f)
		self.tagInfoTimer = wx.Timer()
		self.tagInfoTimer.Bind(wx.EVT_TIMER, globalVars.eventProcess.refreshTagInfo)
		self.nowTime = infoCreator.staticText("0:00:00 / 0:00:00", sizerFlag=wx.ALL, proportion = 0)

		self.creator.AddSpace(10)

		#トラックバーエリア
		#self.horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL,0, style=wx.EXPAND | wx.LEFT | wx.RIGHT, margin=60)
		self.trackBar, dummy = self.creator.clearSlider(_("トラックバー"), x=1000, sizerFlag=wx.EXPAND | wx.LEFT | wx.RIGHT, proportion=0, margin=60, textLayout=None)
		self.trackBar.SetThumbLength(30)
		self.trackBar.Bind(wx.EVT_KEY_UP, stopArrowPropagation)
		self.trackBar.setScrollCallBack(self.events.onTrackBar)
		self.trackBar.setToolTip(self.sec2TimeStr)

		self.creator.AddSpace(20)

		# リストビューエリア
		self.horizontalCreator = views.ViewCreator.ViewCreator(self.viewMode, self.hPanel, self.creator.GetSizer(), wx.HORIZONTAL, 15, style=wx.EXPAND | wx.LEFT | wx.LEFT | wx.RIGHT, proportion=1, margin=60)
		self.playlistView, self.playlistLabel = self.horizontalCreator.customListCtrl(lampViewObject.playlist, _("プレイリスト") + " (0" + _("件") + ")", style=wx.LC_NO_HEADER, sizerFlag=wx.EXPAND | wx.RIGHT,proportion=2,textLayout=wx.VERTICAL)
		self.playlistView.SetFocus()
		view_manager.listViewSetting(self.playlistView, "playlist")
		self.queueView, self.queueLabel = self.horizontalCreator.customListCtrl(lampViewObject.queue, _("キュー") + " (0" + _("件") + ")", style=wx.LC_NO_HEADER, sizerFlag=wx.EXPAND,proportion=1, textLayout=wx.VERTICAL)
		view_manager.listViewSetting(self.queueView, "queue")

		self.hPanel.Layout()

		lb = wx.StaticText(self.hPanel, label=_("状況"), size=(0,0))
		self.shadowList = wx.ListBox(self.hPanel, size=(0,0))
		view_manager.setValueShadowList(self.shadowList)
		
		# タイマーの呼び出し
		self.timer = wx.Timer(self.hFrame)
		self.timer.Start(100)
		self.hFrame.Bind(wx.EVT_TIMER, self.events.timerEvent, self.timer)

		self.hFrame.Layout()
		self.notification = notificationText.notification(self.hPanel)

		self.applyHotKey()

	def applyHotKey(self):
		self.hotkey = hotkeyHandler.HotkeyHandler(None,hotkeyHandler.HotkeyFilter().SetDefault())
		if self.hotkey.addFile(constants.KEYMAP_FILE_NAME,["HOTKEY"])==errorCodes.OK:
			errors=self.hotkey.GetError("HOTKEY")
			if errors:
				tmp=_(constants.KEYMAP_FILE_NAME+"で設定されたホットキーが正しくありません。キーの重複、存在しないキー名の指定、使用できないキーパターンの指定などが考えられます。以下のキーの設定内容をご確認ください。\n\n")
				for v in errors:
					tmp+=v+"\n"
				dialog(_("エラー"),tmp)
			self.hotkey.Set("HOTKEY",self.hFrame)

	def val2vol(self, val):
		return "%d%%" %(round(val))

	def sec2TimeStr(self, sec):
		i = int(sec)
		hour = 0
		min = 0
		sec = 0
		if i > 0: hour = i // 3600
		if i-(hour*3600) > 0: min = (i - hour * 3600) // 60
		if i-(hour*3600)-(min*60) > 0: sec = i - (hour*3600) - (min*60)
		return f"{hour:01}:{min:02}:{sec:02}"

	def GetKeyEntries(self):
		return self.menu.keymap.GetEntries(self.identifier)


class Menu(BaseMenu):
	def __init__(self, identifier, event):
		super().__init__(identifier)
		self.event = event
	
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hFunctionMenu = wx.Menu()
		self.hPlaylistMenu=wx.Menu()
		self.hOperationMenu=wx.Menu()
		self.hSettingsMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()

		#ファイルメニューの中身
		self.RegisterMenuCommand(self.hFileMenu,
			["FILE_OPEN", "DIR_OPEN", "URL_OPEN", "M3U_OPEN", "NEW_M3U8_SAVE", "M3U8_SAVE", "M3U_ADD", "M3U_CLOSE", "EXIT"])
		self.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), False)
		self.hFileMenu.Enable(menuItemsStore.getRef("M3U_CLOSE"), False)
		
		#機能メニューの中身
		#フィルタ設定
		self.hFilterSubMenu = wx.Menu()
		self.RegisterMenuCommand(self.hFilterSubMenu, ["FILTER_SETTING"])
		self.RegisterMenuCommand(self.hFunctionMenu, "FILTER_SUB", None, self.hFilterSubMenu)
		self.RegisterMenuCommand(self.hFunctionMenu, ["SET_SLEEPTIMER", "SET_EFFECTOR", "SET_CURSOR_PLAYING", "ABOUT_PLAYING", "SHOW_NET_CONTROLLER", "SHOW_NET_FILE_MANAGER"])
		self.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
		self.hFunctionMenu.Enable(menuItemsStore.getRef("SET_CURSOR_PLAYING"), False)
		
		# プレイリストメニューの中身
		self.RegisterMenuCommand(self.hPlaylistMenu, ["SET_STARTUPLIST", "PLAYLIST_HISTORY_LABEL"])
		self.hPlaylistMenu.Enable(menuItemsStore.getRef("PLAYLIST_HISTORY_LABEL"), False)
		
		#操作メニューの中身
		self.RegisterMenuCommand(self.hOperationMenu, ["PLAY_PAUSE", "STOP", "PREVIOUS_TRACK", "NEXT_TRACK"])
		skipRtn = settings.getSkipInterval()
		self.RegisterMenuCommand(self.hOperationMenu, {"SKIP": skipRtn[1]+" "+_("進む"), "REVERSE_SKIP": skipRtn[1]+" "+_("戻る")})
		#スキップ間隔設定
		self.hSkipIntervalSubMenu = wx.Menu()
		self.RegisterMenuCommand(self.hSkipIntervalSubMenu, ["SKIP_INTERVAL_INCREASE", "SKIP_INTERVAL_DECREASE"])
		self.RegisterMenuCommand(self.hOperationMenu, "SET_SKIP_INTERVAL_SUB", None, self.hSkipIntervalSubMenu)
		#音量
		self.hVolumeSubMenu = wx.Menu()
		self.RegisterMenuCommand(self.hVolumeSubMenu, ["VOLUME_100", "VOLUME_UP", "VOLUME_DOWN", "MUTE"])
		self.RegisterMenuCommand(self.hOperationMenu, "SET_VOLUME_SUB",  None, self.hVolumeSubMenu)
		#リピート・ループ
		self.hRepeatLoopSubMenu = wx.Menu()
		self.RegisterMenuCommand(self.hOperationMenu, "SET_REPEAT_LOOP_SUB", None, self.hRepeatLoopSubMenu)
		self.RegisterRadioMenuCommand(self.hRepeatLoopSubMenu, "REPEAT_LOOP_NONE")
		self.RegisterRadioMenuCommand(self.hRepeatLoopSubMenu, "RL_REPEAT")
		self.RegisterRadioMenuCommand(self.hRepeatLoopSubMenu, "RL_LOOP")
		if globalVars.eventProcess.repeatLoopFlag == 1: self.hRepeatLoopSubMenu.Check(menuItemsStore.getRef("RL_REPEAT"), True)
		elif globalVars.eventProcess.repeatLoopFlag == 2: self.hRepeatLoopSubMenu.Check(menuItemsStore.getRef("RL_LOOP"), True)
		self.RegisterCheckMenuCommand(self.hOperationMenu, "SHUFFLE")
		if globalVars.eventProcess.shuffleCtrl != None: self.hOperationMenu.Check(menuItemsStore.getRef("SHUFFLE"), True)
		self.RegisterCheckMenuCommand(self.hOperationMenu, "MANUAL_SONG_FEED")
		
		# 設定メニューの中身
		self.hDeviceSubMenu = wx.Menu()
		self.RegisterMenuCommand(self.hSettingsMenu, "SET_DEVICE_SUB", _("再生出力先の変更"), self.hDeviceSubMenu)
		self.RegisterMenuCommand(self.hSettingsMenu,
			["FILE_ASSOCIATE", "SET_SENDTO", "SET_KEYMAP", "SET_HOTKEY", "ENVIRONMENT"])
		self.hPlaylistMenu.Enable(menuItemsStore.getRef("SET_STARTUPLIST"), False)

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu, ["HELP", "CHECK_UPDATE", "VERSION_INFO"])

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F)"))
		self.hMenuBar.Append(self.hFunctionMenu, _("機能(&U)"))
		self.hMenuBar.Append(self.hPlaylistMenu,_("プレイリスト(&P)"))
		self.hMenuBar.Append(self.hOperationMenu,_("操作(&O)"))
		self.hMenuBar.Append(self.hSettingsMenu,_("設定(&S)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
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
			d = views.mkOpenDialog.Dialog("fileOpenDialog")
			d.Initialize(0) #0=ファイルダイアログ
			rtnCode = d.Show()
			if rtnCode == d.PLAYLIST:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.playlistView)
			elif rtnCode == d.QUEUE:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.queueView)
			else:
				return
		elif selected==menuItemsStore.getRef("DIR_OPEN"):
			d = views.mkOpenDialog.Dialog("directoryOpenDialog")
			d.Initialize(1) #1=フォルダダイアログ
			rtnCode = d.Show()
			if rtnCode == d.PLAYLIST:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.playlistView)
			elif rtnCode == d.QUEUE:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.queueView)
			else:
				return
		elif selected==menuItemsStore.getRef("URL_OPEN"):
			d= views.mkOpenDialog.Dialog("urlOpenDialog")
			d.Initialize(2) #2=URLダイアログ
			rtnCode = d.Show()
			if rtnCode == d.PLAYLIST:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.playlistView)
			elif rtnCode == d.QUEUE:
				listManager.addItems([d.GetValue()], globalVars.app.hMainView.queueView)
			else:
				return
		elif selected==menuItemsStore.getRef("M3U_OPEN"):
			m3uManager.loadM3u()
		elif selected==menuItemsStore.getRef("NEW_M3U8_SAVE"):
			m3uManager.saveM3u8()
		elif selected==menuItemsStore.getRef("M3U8_SAVE"):
			m3uManager.saveM3u8(globalVars.listInfo.playlistFile)
		elif selected==menuItemsStore.getRef("M3U_ADD"):
			m3uManager.loadM3u(None, m3uManager.ADD)
		elif selected==menuItemsStore.getRef("M3U_CLOSE"):
			m3uManager.closeM3u()
		elif selected == menuItemsStore.getRef("EXIT"):
			self.parent.hFrame.Close()
		#機能メニューのイベント
		elif selected >= constants.FILTER_LIST_MENU and selected < constants.FILTER_LIST_MENU + 500:
			globalVars.filter.get(selected - constants.FILTER_LIST_MENU).setEnable(event.IsChecked())
		elif selected == menuItemsStore.getRef("FILTER_SETTING"):
			d = filterSettingDialog.Dialog(*globalVars.filter.getDic())
			d.Initialize()
			if d.Show()==wx.ID_CANCEL:
				return
			globalVars.filter.loadDic(*d.GetValue())
		elif selected == menuItemsStore.getRef("SET_SLEEPTIMER"):
			globalVars.sleepTimer.set()
		elif selected == menuItemsStore.getRef("SET_EFFECTOR"):
			effector.effector()
		elif selected == menuItemsStore.getRef("SET_CURSOR_PLAYING"):
			if globalVars.eventProcess.playingList == constants.PLAYLIST:
				p = self.parent.playlistView
				p.Focus(p.getPointer())
				p.Select(-1, 0)
				p.Select(p.getPointer())
			else:
				globalVars.app.hMainView.notification.show(_("プレイリスト上の項目を再生していません。"), 2)
		elif selected == menuItemsStore.getRef("ABOUT_PLAYING"):
			if globalVars.eventProcess.playingList == constants.PLAYLIST:
				listManager.infoDialog(listManager.getTuple(constants.PLAYLIST))
			else:
				listManager.infoDialog(globalVars.listInfo.playingTmp)
		elif selected == menuItemsStore.getRef("SHOW_NET_CONTROLLER"):
			globalVars.lampController.showController()
		elif selected == menuItemsStore.getRef("SHOW_NET_FILE_MANAGER"):
			netFileManager.run();
		# 操作メニューのイベント
		elif selected==menuItemsStore.getRef("PLAY_PAUSE"):
			globalVars.eventProcess.playButtonControl()
		elif selected==menuItemsStore.getRef("STOP"):
			globalVars.eventProcess.stop()
		elif selected==menuItemsStore.getRef("PREVIOUS_TRACK"):
			globalVars.eventProcess.previousBtn()
		elif selected==menuItemsStore.getRef("NEXT_TRACK"):
			globalVars.eventProcess.nextFile(button=True)
		elif selected==menuItemsStore.getRef("VOLUME_100"):
			globalVars.eventProcess.changeVolume(vol=100)
		elif selected==menuItemsStore.getRef("VOLUME_UP"):
			globalVars.eventProcess.changeVolume(+1)
		elif selected==menuItemsStore.getRef("VOLUME_DOWN"):
			globalVars.eventProcess.changeVolume(-1)
		elif selected==menuItemsStore.getRef("MUTE"):
			globalVars.eventProcess.mute()
		elif selected==menuItemsStore.getRef("FAST_FORWARD"):
			globalVars.play.fastForward()
		elif selected==menuItemsStore.getRef("REWIND"):
			globalVars.play.rewind()
		elif selected==menuItemsStore.getRef("SAY_TIME"):
			pos = globalVars.play.getPosition()
			if pos == -1: time = _("情報がありません")
			else:
				hour = pos // 3600
				min = (pos - hour * 3600) // 60
				sec = int(pos - hour * 3600 - min * 60)
				if hour == 0: sHour = ""
				else: sHour = str(int(hour)) + _("時間") + " "
				if min == 0: sMin = ""
				else: sMin = str(int(min)) + _("分") + " "
				time = sHour + sMin + str(int(sec)) + _("秒")
			globalVars.app.say(time)
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
		elif selected==menuItemsStore.getRef("MANUAL_SONG_FEED"):
			globalVars.eventProcess.setSongFeed()
		elif selected >= constants.DEVICE_LIST_MENU and selected < constants.DEVICE_LIST_MENU + 500:
			if selected == constants.DEVICE_LIST_MENU: globalVars.play.setDevice(PLAYER_DEFAULT_SPEAKER)
			else: globalVars.play.setDevice(selected - constants.DEVICE_LIST_MENU)
		elif selected >= constants.PLAYLIST_HISTORY and selected < constants.PLAYLIST_HISTORY+ 20:
			m3uManager.loadM3u(globalVars.m3uHistory.getList()[selected - constants.PLAYLIST_HISTORY])
		elif selected==menuItemsStore.getRef("SET_STARTUPLIST"):
			startupListSetter.run()
		elif selected==menuItemsStore.getRef("FILE_ASSOCIATE"):
			fileAssocDialog.assocDialog()
		elif selected==menuItemsStore.getRef("SET_SENDTO"):
			sendToManager.sendToCtrl("LAMP")
		elif selected==menuItemsStore.getRef("SET_KEYMAP"):
			if self.setKeymap("MainView",_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
				#ショートカットキーの変更適用とメニューバーの再描画
				self.parent.menu.InitShortcut()
				self.parent.menu.ApplyShortcut(self.parent.hFrame)
				self.parent.menu.Apply(self.parent.hFrame)
		elif selected==menuItemsStore.getRef("SET_HOTKEY"):
			if self.setKeymap("HOTKEY",_("グローバルホットキーの設定"),self.parent.hotkey,filter=self.parent.hotkey.filter):
				#変更適用
				self.parent.hotkey.UnSet("HOTKEY",self.parent.hFrame)
				self.parent.applyHotKey()
		elif selected==menuItemsStore.getRef("ENVIRONMENT"):
			d = setting_dialog.settingDialog("environment_dialog")
			d.Initialize()
			d.Show()
		elif selected==menuItemsStore.getRef("HELP"):
			if os.path.exists("./readme.txt"): subprocess.Popen("start ./readme.txt", shell=True)
			else: dialog(_("ヘルプ"), _("ヘルプファイルが見つかりません。"))
		elif selected==menuItemsStore.getRef("CHECK_UPDATE"):
			update.checkUpdate()
		elif selected==menuItemsStore.getRef("VERSION_INFO"):
			versionDialog.versionDialog()

	def setKeymap(self, identifier,ttl,keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier.upper()].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		entries=[]
		for map in (self.parent.menu.keymap,self.parent.hotkey):
			for i in map.entries.keys():
				if identifier.upper()!=i:	#今回の変更対象以外のビューのものが対象
					entries.extend(map.entries[i])

		d=views.globalKeyConfig.Dialog(keyData,menuData,entries,filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		result={}
		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		newMap.write()
		return True

	def OnMenuOpen(self, event):
		menuObject = event.GetEventObject()
		
		if event.GetMenu()==self.parent.menu.hDeviceSubMenu:
			menu = self.parent.menu.hDeviceSubMenu
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
		elif menuObject == self.parent.menu.hPlaylistMenu:
			menu = self.parent.menu.hPlaylistMenu
			# 履歴部分を削除
			for i in range(menu.GetMenuItemCount() - 2):
				menu.DestroyItem(menu.FindItemByPosition(2))
			# 履歴部分を作成
			index = 0
			for path in globalVars.m3uHistory.getList():
				menu.Insert(2, constants.PLAYLIST_HISTORY + index, path)
				index += 1
		elif menuObject == self.parent.menu.hFilterSubMenu:
			menu = self.parent.menu.hFilterSubMenu
			# いったん全て削除
			for i in range(menu.GetMenuItemCount() - 1):
				menu.DestroyItem(menu.FindItemByPosition(0))
			# 項目を作成
			index = 0
			for filter in globalVars.filter.getList():
				menu.InsertCheckItem(index, constants.FILTER_LIST_MENU + index, filter.getName())
				menu.Check(constants.FILTER_LIST_MENU + index, filter.isEnable())
				index += 1

		elif menuObject == self.parent.menu.hOperationMenu:
			self.parent.menu.hOperationMenu.Check(menuItemsStore.getRef("MANUAL_SONG_FEED"), globalVars.app.config.getboolean("player", "manualSongFeed", False))

	def onButtonClick(self, event):
			if event.GetEventObject() == globalVars.app.hMainView.previousBtn:
				globalVars.eventProcess.previousBtn()
			elif event.GetEventObject() == globalVars.app.hMainView.playPauseBtn:
				globalVars.eventProcess.playButtonControl()
			elif event.GetEventObject() == globalVars.app.hMainView.nextBtn:
				globalVars.eventProcess.nextFile(button=True)
			elif event.GetEventObject() == globalVars.app.hMainView.stopBtn:
				globalVars.eventProcess.stop()
			elif event.GetEventObject() == globalVars.app.hMainView.repeatLoopBtn:
				globalVars.eventProcess.repeatLoopCtrl()
			elif event.GetEventObject() == globalVars.app.hMainView.shuffleBtn:
				globalVars.eventProcess.shuffleSw()
			elif event.GetEventObject() == globalVars.app.hMainView.muteBtn:
				globalVars.eventProcess.mute()

	def onVolumeSlider(self):
		val = globalVars.app.hMainView.volumeSlider.GetValue()
		globalVars.eventProcess.changeVolume(vol=val)

	def onTrackBar(self):
		globalVars.eventProcess.trackBarCtrl(self.parent.trackBar)

	def timerEvent(self, evt):
		globalVars.eventProcess.refreshView()

	def OnExit(self, event=None):
		if globalVars.app.config.getboolean("player", "fadeOutOnExit", False) and globalVars.play.getStatus() == PLAYER_STATUS_PLAYING:
			while globalVars.play.setVolumeByDiff(-2):
				time.sleep(0.07)
		if not m3uManager.closeM3u(newSave=False): return
		globalVars.app.hMainView.timer.Stop()
		globalVars.app.hMainView.timer.Destroy()
		globalVars.app.hMainView.tagInfoTimer.Stop()
		globalVars.app.hMainView.tagInfoTimer.Destroy()
		self.parent.notification.destroy()
		globalVars.play.exit()
		globalVars.lampController.exit()
		super().OnExit(event)
