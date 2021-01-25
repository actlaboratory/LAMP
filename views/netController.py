# -*- coding: utf-8 -*-
# networkController
# Copyright (C) 2021 Hiroki Fujii <hfujii@hisystron.com>

import wx
import os
import win32api
import requests
import fxManager
from views import mkDialog

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

def show():
    d = Dialog("networkController")
    d.Initialize()
    return d.Show()

class Dialog(BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("LAMP Controller設定"))
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
        self.creator.staticText(_("このLAMPは、コントローラに登録されていません。"))
        
        # ログイン情報
        self.userName, dummy = self.creator.inputbox(_("ユーザー名"), textLayout=wx.HORIZONTAL)
        self.password, dummy = self.creator.inputbox(_("パスワード"), textLayout=wx.HORIZONTAL)
        self.displayName, dummy = self.creator.inputbox(_("LAMPの名前"), textLayout=wx.HORIZONTAL)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.newEntryBtn = self.creator.button(_("このLAMPを新規登録"),self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("閉じる"), self.onButtonClick)
        return
    
    def onButtonClick(self, evt):
        if evt.GetEventObject()==self.newEntryBtn:
            if self.__entry(): self.wnd.EndModal(wx.ID_OPEN)
        elif evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)

    def __entry(self):
        obj = {"authentication": {"userName": self.userName.GetValue(), "password": self.password.GetValue()},
            "software": {"driveSerialNo": win32api.GetVolumeInformation(os.environ["SystemRoot"][:3])[1], "pcName": os.environ["COMPUTERNAME"], "displayName": self.displayName.GetValue()}, "apiVersion": constants.API_VERSION}
        try:
            rp = requests.post("http://localhost:8091/lamp/api/v1/entry", json=obj)
            print(rp.text)
            j = rp.json()
            if j["code"] == 200:
                globalVars.app.config["network"]["user_name"] = self.userName.GetValue()
                globalVars.app.config["network"]["software_key"] = j["softwareKey"]
                d = mkDialog.Dialog("entry success dialog")
                d.Initialize(_("登録完了"), _("このLAMPは、LAMP Controllerに登録されました。"), ["OK"], False)
                fxManager.confirm()
                d.Show()
                return True
            elif j["code"] == 400 and j["reason"] == "invalid display name":
                d = mkDialog.Dialog("invalidDisplayNameDialog")
                d.Initialize(_("登録失敗"), _("LAMPの名前は、1文字以上、30文字以内で指定してください。"), ["OK"], False)
                fxManager.error()
                d.Show()
                return False
            elif j["code"] == 400 and j["reason"] == "authentication faild":
                d = mkDialog.Dialog("authErrorDialog")
                d.Initialize(_("認証失敗"), _("ユーザー名、またはパスワードが謝っています。"), ["OK"], False)
                fxManager.error()
                d.Show()
                return False
            else:
                d = mkDialog.Dialog("entryErrorDialog")
                d.Initialize(_("登録失敗"), _("LAMPの登録に失敗しました。ネットワーク接続などを確認してください。"), ["OK"], False)
                fxManager.error()
                d.Show()
                return False
        except Exception as e:
            print(str(e))
            d = mkDialog.Dialog("entryErrorDialog")
            d.Initialize(_("登録失敗"), _("LAMPの登録に失敗しました。ネットワーク接続などを確認してください。"), ["OK"], False)
            fxManager.error()
            d.Show()
            return False

