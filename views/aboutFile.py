# -*- coding: utf-8 -*-
# sleepTimer

import wx
import os

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self):
        self.identifier=_("ファイル情報") #このビューを表す文字列
        self.log=getLogger(self.identifier)
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("ファイル情報"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.iText,self.static=self.creator.inputbox(_("ファイルの場所"),400, "", 1, 2)
        self.bCancel = self.creator.cancelbutton(_("閉じる"), self.onButtonClick)

    def GetData(self):
        return None

    def onButtonClick(self, evt):
        if evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)
