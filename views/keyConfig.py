# -*- coding: utf-8 -*-
#Falcon key config view
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import wx

import globalVars
import keymap
import views.ViewCreator

from logging import getLogger
from views.baseDialog import *

TIMER_INTERVAL=100

class Dialog(BaseDialog):
	def __init__(self,parent,filter=None):
		super().__init__("keyConfigDialog")
		self.parent=parent				#親ウィンドウ
		self.filter=filter				#キーフィルタ
		if self.filter==None:			#キーフィルタ未指定ならデフォルトとしてメインビューで設定されたキーフィルタを適用
			self.filter=globalVars.app.hMainView.menu.keymap.filter

		self.result=""					#取得した入力キー(結果格納・外部参照用)
		self.key=""						#取得した入力キー(内部処理用)
		self.timer=None					#wx.Timerオブジェクト

	def Initialize(self):
		super().Initialize(self.parent,_("キー設定"))
		self.wnd.Bind(wx.EVT_TIMER, self.OnTimer)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.mainArea=views.ViewCreator.BoxSizer(self.sizer,wx.HORIZONTAL,wx.ALIGN_CENTER)

		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.mainArea,wx.VERTICAL,20)
		self.creator.staticText(_("設定したいキーの組み合わせを押してください..."))
		self.keyNameText=self.creator.staticText("")
		self.errorText=self.creator.staticText("")


		self.buttonArea=views.ViewCreator.BoxSizer(self.sizer,wx.HORIZONTAL, wx.ALIGN_RIGHT)
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.buttonArea,wx.HORIZONTAL,20)
		self.bCancel=self.creator.cancelbutton(_("設定解除"),None)

	def Show(self):
		self.panel.Layout()
		self.sizer.Fit(self.wnd)
		self.wnd.Centre()
		self.timer=wx.Timer(self.wnd)
		self.timer.Start(TIMER_INTERVAL)
		result=self.wnd.ShowModal()
		if result!=wx.ID_CANCEL:
			self.value=self.GetData()
		self.Destroy()
		return result


	def GetData(self):
		return self.result

	def OnTimer(self,event):
		self.timer.Stop()

		#キーの判定
		hits=[]
		for name in self.filter.GetUsableKeys():
			#マウス関連は利用不可
			code=keymap.str2key[name]
			if code<=4:
				continue
			#カテゴリキーは取得不可、NumLockとCapsLockは押し下げ状態ではなく現在のON/OFFを返してしまうので
			if type(code)==wx.KeyCategoryFlags or name=="NUMLOCK" or name=="SCROLL":
				continue
			if wx.GetKeyState(code):
				hits.append(name)

		if hits:
			self.key=""
			for i,key in enumerate(hits):
				self.key+=key
				if i<len(hits)-1:
					self.key+="+"
			if len(self.result)<len(self.key):
				self.result=self.key
			self.keyNameText.SetLabel(self.result)
		else:									#キーが放されたら前の入力を検証する
			if self.result!="":
				if self.filter.Check(self.result):
					self.wnd.EndModal(wx.ID_OK)		#正しい入力なのでダイアログを閉じる
					return
				else:
					self.errorText.SetLabel(self.filter.GetLastError())
					globalVars.app.say(self.filter.GetLastError(),True)

				self.key=""
				self.result=""
		self.timer.Start(TIMER_INTERVAL)
		return

