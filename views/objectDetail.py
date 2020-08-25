# -*- coding: utf-8 -*-
#Falcon object detail view
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def Initialize(self,dic):
		self.identifier="objectDetailDialog"#このビューを表す文字列
		self.log=getLogger("falcon.%s" % self.identifier)
		self.log.debug("created")
		self.app=globalVars.app
		super().Initialize(self.app.hMainView.hFrame,_("このファイルについて"))
		self.InstallControls(dic)
		return True

	def InstallControls(self,dic):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,views.ViewCreator.FlexGridSizer,20)

		for title,content in dic.items():
			self.iName,self.static=self.creator.inputbox(title,400,str(content),style=wx.TE_READONLY)

		self.buttonArea=views.ViewCreator.BoxSizer(self.sizer,wx.HORIZONTAL, wx.ALIGN_RIGHT)
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.buttonArea,wx.HORIZONTAL,20)
		self.bOk=self.creator.okbutton(_("ＯＫ"),None)

	def GetValue(self):
		return None
