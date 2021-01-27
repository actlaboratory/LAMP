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
    try:
        responseObject = requests.post("http://localhost:8091/lamp/api/v1/softwaremanage", json=globalVars.lampController.makeData(), timeout=5)
        responseObject.encoding="utf-8"
        resJson = responseObject.json()
        if (resJson["code"] == 200 and resJson["displayName"]) or (resJson["code"] == 400 and resJson["reason"]):
            pass
    except Exception as e:
        resJson = False
    
    if resJson != False and resJson["code"] == 400 and "authentication faild" in resJson["reason"]:
        d = Dialog("networkController")
        d.Initialize()
        return d.Show()
    elif resJson != False and resJson["code"] == 200:
        d = Dialog("networkController")
        d.Initialize(True, resJson)
        return d.Show()
    else:
        d = mkDialog.Dialog("connectionFaildDialog")
        d.Initialize(_("通信失敗"), _("登録状況の確認に失敗しました。\nネットワーク接続などを確認してください。"), ["OK"], False)
        fxManager.error()
        d.Show()
        return wx.ID_CANCEL

class Dialog(BaseDialog):
    def Initialize(self, entered=False, resJson=None):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("LAMP Controller設定"))
        self.entered = entered
        self.resJson = resJson
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        if not self.entered:
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
            self.creator.staticText(_("このLAMPは、コントローラに登録されていません。"), margin=20)
            
            # ログイン情報
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,views.ViewCreator.FlexGridSizer,20,2)
            self.userName, dummy = self.creator.inputbox(_("ユーザー名"), x=450, textLayout=wx.HORIZONTAL)
            self.password, dummy = self.creator.inputbox(_("パスワード"), style=wx.TE_PASSWORD, x=450, textLayout=wx.HORIZONTAL)
            self.displayName, dummy = self.creator.inputbox(_("LAMPの名前"), x=450, textLayout=wx.HORIZONTAL)
            self.pcName, dummy = self.creator.inputbox(_("コンピュータの名前"), defaultValue=os.environ["COMPUTERNAME"], style=wx.TE_READONLY, x=450, textLayout=wx.HORIZONTAL)
            
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
            self.newEntryBtn = self.creator.button(_("このLAMPを新規登録"),self.onButtonClick)
            self.bCancel = self.creator.cancelbutton(_("閉じる"), self.onButtonClick)
        else:
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
            self.creator.staticText(_("このLAMPは、コントローラに登録されています。"), margin=20)
            
            # 情報表示
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,views.ViewCreator.FlexGridSizer,20,2)
            self.lampName, dummy = self.creator.inputbox(_("LAMPの名前"), defaultValue=str(self.resJson["displayName"]), style=wx.TE_READONLY, x=450, textLayout=wx.HORIZONTAL)
            self.pcName, dummy = self.creator.inputbox(_("コンピュータの名前"), defaultValue=os.environ["COMPUTERNAME"], style=wx.TE_READONLY, x=450, textLayout=wx.HORIZONTAL)

            # 設定パネル
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
            self.clientConfigCheck = self.creator.checkbox(_("LAMP Controllerからの操作を有効にする"))
            
            self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
            self.releaseBtn = self.creator.button(_("このLAMPを登録解除"),self.onButtonClick)
            self.bCancel = self.creator.cancelbutton(_("閉じる"), self.onButtonClick)
        return
    
    def onButtonClick(self, evt):
        if self.entered == False and evt.GetEventObject()==self.newEntryBtn:
            if self.__entry(): self.wnd.EndModal(wx.ID_OPEN)
        elif self.entered and evt.GetEventObject()==self.releaseBtn:
            if self.__release(): self.wnd.EndModal(wx.ID_CLOSE)
        elif evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)

    def __release(self):
        try:
            json = globalVars.lampController.makeData()
            json["operation"] = "release"
            rp = requests.post("http://localhost:8091/lamp/api/v1/softwaremanage", json=json, timeout=30)
            j = rp.json()
            if j["code"] == 200: release = True
            else: release = False
        except Exception as e:
            release = False
        
        if release:
            globalVars.app.config["network"]["user_name"] = ""
            globalVars.app.config["network"]["software_key"] = ""
            d = mkDialog.Dialog("entry success dialog")
            d.Initialize(_("完了"), _("このLAMPの登録を解除しました。"), ["OK"], False)
            fxManager.confirm()
            d.Show()
            return True
        else:
            d = mkDialog.Dialog("invalidDisplayNameDialog")
            d.Initialize(_("通信失敗"), _("LAMPの登録を解除できませんでした。\nネットワーク接続などを確認してください。"), ["OK"], False)
            fxManager.error()
            d.Show()
            return False
    
    def __entry(self):
        obj = {"authentication": {"userName": self.userName.GetValue(), "password": self.password.GetValue()},
            "software": {"driveSerialNo": win32api.GetVolumeInformation(os.environ["SystemRoot"][:3])[1], "pcName": os.environ["COMPUTERNAME"], "displayName": self.displayName.GetValue()}, "apiVersion": constants.API_VERSION}
        try:
            rp = requests.post("http://localhost:8091/lamp/api/v1/entry", json=obj)
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
            elif j["code"] == 400 and j["reason"] == "already entered":
                d = mkDialog.Dialog("invalidDisplayNameDialog")
                d.Initialize(_("登録失敗"), _("このLAMPは、すでに登録されています。"), ["OK"], False)
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
            d = mkDialog.Dialog("entryErrorDialog")
            d.Initialize(_("登録失敗"), _("LAMPの登録に失敗しました。ネットワーク接続などを確認してください。"), ["OK"], False)
            fxManager.error()
            d.Show()
            return False

