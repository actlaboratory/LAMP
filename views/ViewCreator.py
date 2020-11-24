# -*- coding: utf-8 -*-
#View Creator
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>

import wx
import win32api
import _winxptheme

import views.lampViewObject

from views import ViewCreatorBase
from views.ViewCreatorBase import *

class ViewCreator(ViewCreatorBase):
	def __init__(self, *pArg, **kArg):
		super().__init__(*pArg, **kArg)

		# 標準オブジェクトの変更が必要ならば記述
		# self.winObject["object_name"] = newObject

	def customListCtrl(self,lcObject, text, event=None, style=0, size=(200,200), sizerFlag=wx.ALL, proportion=0,margin=5,textLayout=wx.DEFAULT):
		hStaticText,sizer,parent=self._addDescriptionText(text,textLayout,sizerFlag, proportion,margin)

		hListCtrl=lcObject(parent,wx.ID_ANY,style=style | wx.BORDER_RAISED, size=size)
		hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED,event)
		self._setFace(hListCtrl)
		self._setFace(hListCtrl.GetMainWindow())
		_winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(),0x101F,0,0),"","")#ヘッダーのウィンドウテーマを引っぺがす
		Add(sizer,hListCtrl,proportion,sizerFlag,margin)
		self.AddSpace()
		return hListCtrl,hStaticText
