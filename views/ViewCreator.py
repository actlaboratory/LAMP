# -*- coding: utf-8 -*-
#View Creator
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import wx
import win32api
import _winxptheme
from views import ViewCreatorBase

NORMAL=0
BUTTON_COLOUR=1
SKIP_COLOUR=2

GridSizer = -1
FlexGridSizer = -2

MODE_WHITE=0
MODE_DARK=1

class ViewCreator(ViewCreatorBase.ViewCreatorBase):
	def __init__(self, *pArg, **kArg):
		# wxオブジェクトの入れ替えが必要ならば記述
		# 136
		# [object] = newObject

		super().__init__(*pArg, **kArg)

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


#parentで指定したsizerの下に、新たなBoxSizerを設置
def BoxSizer(parent,orient=wx.VERTICAL,flg=0,border=0):
	sizer=wx.BoxSizer(orient)
	if (parent!=None):
		parent.Add(sizer,0,flg,border)
	return sizer

def Add(sizer, window, proportion=0, flag=0, border=0, expandFlag=None):
	if isinstance(sizer,wx.BoxSizer):
		if sizer.Orientation==wx.VERTICAL:
			for i in (wx.ALIGN_TOP , wx.ALIGN_BOTTOM , wx.ALIGN_CENTER_VERTICAL):
				if flag&i==i:flag-=i
		else:
			for i in (wx.ALIGN_LEFT , wx.ALIGN_RIGHT , wx.ALIGN_CENTER_HORIZONTAL , wx.ALIGN_CENTER):
				if flag&i==i:flag-=i
	if expandFlag==wx.HORIZONTAL:	#幅を拡張
		if type(sizer) in (wx.BoxSizer,wx.StaticBoxSizer) and sizer.GetOrientation()==wx.VERTICAL:
			sizer.Add(window,proportion,flag | wx.EXPAND, border)
		else:
			sizer.Add(window,1,flag,border)
	else:
		sizer.Add(window,proportion,flag,border)

# parentで指定されたフレームにパネルを設置する
def makePanel(parent):
	hPanel=wx.Panel(parent,wx.ID_ANY,size=(-1,-1))
	return hPanel


class TextCtrl(wx.TextCtrl):
	def AcceptsFocusFromKeyboard(self):
		return True
