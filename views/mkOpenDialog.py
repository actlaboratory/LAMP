# -*- coding: utf-8 -*-
# sample dialog

import wx
import re
import os
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self, type): #0=ファイル、1=フォルダ選択ダイアログ
        self.type=type
        self.log.debug("created")
        if type==0:
            super().Initialize(self.app.hMainView.hFrame,_("ファイルを開く"))
        elif type==1:
            super().Initialize(self.app.hMainView.hFrame,_("フォルダを開く"))
        elif type==2:
            super().Initialize(self.app.hMainView.hFrame,_("URLを開く"))
        self.InstallControls()

        #定数
        self.PLAYLIST = 0
        self.QUEUE = 1

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        guideTexts=[_("ファイルの場所を指定"),_("フォルダの場所を指定"),_("URLを指定")]

        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL | wx.EXPAND,margin=20)
        self.iText,self.static=self.creator.inputbox(guideTexts[self.type], x=-1,proportion=1,textLayout=wx.VERTICAL,margin=0)
        if self.type<=1:
            self.browse=self.creator.button(_("参照"),self.onBrowseBtn,sizerFlag=wx.ALIGN_BOTTOM | wx.BOTTOM,margin=3)
            self.browse.SetFocus()

        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT | wx.ALL,margin=20)
        self.playlistBtn=self.creator.button(_("プレイリストに追加"),self.onButtonClick,proportion=1)
        self.playlistBtn.SetDefault()        
        self.queueBtn=self.creator.button(_("キューに追加"),self.onButtonClick,proportion=1)
        self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

        self.panel.Layout()

    def GetData(self):
        return self.iText.GetLineText(0)

    def onBrowseBtn(self, evt):
        if self.type==0:
            d = wx.FileDialog(None, _("ファイルを選択"), style=wx.FD_OPEN)
            d.ShowModal()
        elif self.type==1:
            d = wx.DirDialog(None, _("フォルダを選択"))
            d.ShowModal()
        self.iText.SetLabel(d.GetPath())

    def onButtonClick(self, evt):
        if os.path.exists(self.GetData())==False and self.type != 2: #URI以外のファイルパスエラー
            return None
        elif re.search("https?://.+\..+", self.GetData()) == None and self.type == 2: #URLエラー
            return None
        if evt.GetEventObject()==self.playlistBtn:
            code = self.PLAYLIST
        elif evt.GetEventObject()==self.queueBtn:
            code = self.QUEUE
        self.wnd.EndModal(code)
        