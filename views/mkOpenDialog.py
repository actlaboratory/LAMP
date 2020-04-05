# -*- coding: utf-8 -*-
# sample dialog

import wx
import os
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self, type): #0=ファイル、1=フォルダ選択ダイアログ
        self.type=type
        self.identifier="openDialog"#このビューを表す文字列
        self.log=getLogger(self.identifier)
        self.log.debug("created")
        if type==0:
            super().Initialize(self.app.hMainView.hFrame,_("ファイルを開く"))
        elif type==1:
            super().Initialize(self.app.hMainView.hFrame,_("フォルダを開く"))
        self.InstallControls()

        #定数
        self.PLAYLIST = 0
        self.QUEUE = 1

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.VERTICAL,20)
        if self.type==0:
            self.iText,self.static=self.creator.inputbox(_("ファイルの場所を指定"),400)
            self.browse=self.creator.button(_("参照"),self.onBrowseBtn)
        elif self.type==1:
            self.iText,self.static=self.creator.inputbox(_("フォルダの場所を指定"),400)
            self.browse=self.creator.button(_("参照"),self.onBrowseBtn)

        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self.playlistBtn=self.creator.button(_("プレイリストに追加"),self.onButtonClick)
        self.queueBtn=self.creator.button(_("キューに追加"),self.onButtonClick)
        self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

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
        if os.path.exists(self.iText.GetLabel())==False:
            return None
        if evt.GetEventObject()==self.playlistBtn:
            code = self.PLAYLIST
        elif evt.GetEventObject()==self.queueBtn:
            code = self.QUEUE
        self.wnd.EndModal(code)
        