# -*- coding: utf-8 -*-
# sample dialog

import wx
import os
import globalVars
import fxManager
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

def run(errorList, notFoundList):
    if globalVars.app.config.getboolean("notification", "ignoreError", True): return
    d = Dialog("loadErrorDialog")
    d.Initialize(errorList, notFoundList)
    fxManager.error()
    return d.Show()

class Dialog(BaseDialog):
    def Initialize(self, errorList, notFoundList):
        self.title = _("読み込みエラー")
        self.error = errorList
        self.notFound = notFoundList
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,self.title)
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
        self.creator.staticText(_("以下のファイルは、読み込むことができませんでした。"))
        er, erl = self.creator.virtualListCtrl(_("対応していないファイル") + " (" + str(len(self.error)) + _("件") + ")", style=wx.LC_NO_HEADER | wx.LC_SINGLE_SEL, sizerFlag=wx.EXPAND)
        nf, nfl = self.creator.virtualListCtrl(_("見つからなかったファイル") + " (" + str(len(self.notFound)) + _("件") + ")", style=wx.LC_NO_HEADER | wx.LC_SINGLE_SEL, sizerFlag=wx.EXPAND)
        er.AppendColumn("")
        nf.AppendColumn("")
        error = []
        for s in self.error:
            error.append([s])
        er.setList(error)
        notFound = []
        for s in self.notFound:
            notFound.append([s])
        nf.setList(notFound)
        er.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        nf.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bOk = self.creator.cancelbutton("OK")
        self.bOk.SetDefault()

    def GetData(self):
        return None

