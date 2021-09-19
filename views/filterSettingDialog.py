# -*- coding: utf-8 -*-
# filter setting dialog
#Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import re
import wx

import filterManager
import views.KeyValueSettingDialogBase

from simpleDialog import dialog,errorDialog


class Dialog(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def __init__(self,types,patterns,statuses,startups):
		info=[
			(_("名前"),wx.LIST_FORMAT_LEFT,350),
			(_("種別"),wx.LIST_FORMAT_LEFT,370),
			(_("パターン"),wx.LIST_FORMAT_LEFT,200),
			(_("状態"),wx.LIST_FORMAT_LEFT,80),
			(_("起動時"),wx.LIST_FORMAT_LEFT,120),
		]
		typeStrings={}
		for k,v in types.items():
			typeStrings[k]=filterManager.getTypeString(v)
		super().__init__("filterSettingDialog",SettingDialog,info,typeStrings,patterns,statuses,startups)

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,"フィルター設定")
		return

	def SettingDialogHook(self,dialog):
		pass

	def OkButtonEvent(self,event):
		"""
			
		"""
		event.Skip()

	def GetData(self):
		ret = [{},self.values[1],self.values[2],self.values[3]]
		for k,v in self.values[0].items():
			ret[0][k]=filterManager.getType(v)
		return ret

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,name="",type="",pattern="",status=False,startup=False):
		super().__init__(
			parent,
			(
				(_("名前"),True),
				(_("タイプ"),list(filterManager.getTypeStringList())),
				(_("パターン"),True),
				(None,_("有効にする")),
				(None,_("起動時にデフォルトで有効にする"))
			),
			(None,None,None,None,None),
			name,type,pattern,status,startup
		)

	def Initialize(self):
		return super().Initialize(_("フィルターの設定"))

	def test(self,event):
		self.testDialog()

	#正規表現としての妥当性の検証をしておく
	def Validation(self,event):
		try:
			re.compile(self.edits[2].GetLineText(0))
			event.Skip()
		except Exception as e:
			errorDialog(_("入力パターンが不正です。"),self.wnd)

	def GetData(self):
		ret=[None]*len(self.edits)
		ret[0]=self.edits[0].GetLineText(0).lower()			#iniファイルへの保存のためキーは小文字に統一
		ret[1]=self.edits[1].GetString(self.edits[1].GetCurrentSelection())
		ret[2]=self.edits[2].GetLineText(0).lower()			#表現は小文字統一して比較するようになっているため、小文字で保存
		ret[3]=self.edits[3].GetValue()
		ret[4]=self.edits[4].GetValue()
		return ret
