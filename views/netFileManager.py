# -*- coding: utf-8 -*-
# file manager fo lamp controller dialog
# Copyright (C) 2021 Hiroki Fujii <hfujii@hisystron.com>

import wx
import win32api
import os
import time
import threading
import requests
from logging import getLogger
import constants
import globalVars
import fxManager
import views.ViewCreator
from views import mkDialog
from logging import getLogger
from views.baseDialog import *

# 実行用関数
def run():
    netFileManager = Dialog("netFileManager")
    netFileManager.Initialize()
    return netFileManager.Show()


# 管理ディレクトリ画面（メイン）
class Dialog(BaseDialog):
    def Initialize(self):
        self.title = _("LAMP Controllerのファイル")
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,self.title)
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
        self.listCtrl, dummy = self.creator.listCtrl(_("関連付けられたフォルダ"), style=wx.LC_SINGLE_SEL | wx.LC_REPORT, sizerFlag=wx.EXPAND, size=(1000,300))
        self.listCtrl.AppendColumn(_("名前"))
        self.listCtrl.AppendColumn(_("場所"))
        for i in globalVars.app.config["net_associated_file"]:
            self.listCtrl.Append(str(i), globalVars.app.config["net_associated_file"][i])
        self.listCtrl.SetColumnWidth(0, 300)
        self.listCtrl.SetColumnWidth(1, 700)
        
        # リスト書き込み
        for k in globalVars.lampController.netDirDict:
            self.listCtrl.Append((k, globalVars.lampController.netDirDict[k]))

        self.listCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onChangeFocus)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onChangeFocus)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onChangeFocus)

        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bDelete = self.creator.button(_("このLAMPから削除"), self.onButtonClick)
        self.bDelete.Enable(False)
        self.bAdd = self.creator.button(_("このLAMPに追加"), self.onButtonClick)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bUpdate = self.creator.button(_("コントローラの情報を更新"), self.onButtonClick)
        self.bUpdate.Enable(False)
        self.bNew = self.creator.button(_("新しくコントローラに送信"), self.onButtonClick)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bCancel = self.creator.cancelbutton(_("閉じる"))

    def GetData(self):
        return None

    def onChangeFocus(self, evt):
        if self.listCtrl.GetSelectedItemCount() == 1:
            self.bDelete.Enable()
            self.bUpdate.Enable()
        else:
            self.bDelete.Enable(False)
            self.bUpdate.Enable(False)
    
    def onButtonClick(self, event):
        evt = event.GetEventObject()
        if evt == self.bNew:
            self.__new()
        if evt == self.bUpdate:
            self.__update()
        elif evt == self.bAdd:
            self.__add()
        elif evt == self.bDelete:
            self.__delete()

    # 送信ボタン動作
    def __new(self):
        dirDialog = wx.DirDialog(self.wnd)
        if dirDialog.ShowModal() == wx.ID_CANCEL:
            return wx.ID_CANCEL
        else:
            d = netFileSend("netFileSendView")
            d.Initialize(dirDialog.GetPath())
            if d.Show() == wx.ID_CANCEL: return wx.ID_CANCEL
            else:
                ret = d.GetValue()
                # リスト類更新
                globalVars.lampController.netDirDict[ret[0]] = ret[1]
                globalVars.lampController.saveDirDict()
                self.listCtrl.Append(ret)
        self.listCtrl.SetFocus()

    # 情報更新
    def __update(self):
        idx = self.listCtrl.GetFirstSelected()
        name = self.listCtrl.GetItemText(idx, 0)
        path = self.listCtrl.GetItemText(idx, 1)
        if not os.path.isdir(path):
            d = mkDialog.Dialog("directoryError")
            d.Initialize(_("エラー"), _("場所が利用できません。フォルダを確認してください。"), ["OK"], False)
            fxManager.error()
            return d.Show()
        d = netFileSend("netFileSendView")
        d.Initialize(path, name)
        d.Show()
        self.listCtrl.SetFocus()


    # 単純追加ボタン操作
    def __add(self):
        d = netFileAddDialog("manualNetAssocDialog")
        d.Initialize()
        if d.Show() == wx.ID_CANCEL: return
        else:
            ret = d.GetValue()
            globalVars.lampController.netDirDict[ret[0]] = ret[1]
            globalVars.lampController.saveDirDict()
            self.listCtrl.Append(ret)
        self.listCtrl.SetFocus()

    # 削除
    def __delete(self):
        if self.listCtrl.GetSelectedItemCount() == 1:
            i = self.listCtrl.GetFirstSelected()
            iText = self.listCtrl.GetItemText(i)
            if iText in globalVars.lampController.netDirDict:
                del globalVars.lampController.netDirDict[iText]
                globalVars.lampController.saveDirDict()
            self.listCtrl.DeleteItem(i)
            self.listCtrl.SetFocus()

# ファイル情報送信ビュー
class netFileSend(BaseDialog):
    def Initialize(self, path, name=None):
        self.title = _("フォルダ情報送信")
        # 更新処理がときは自動実行
        if name == None: self.setName = False
        else:
            self.setName = True
        self.nameValue = name
        self.path = path
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,self.title)
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
        if self.nameValue == None: #新規そう神事のプロンプト
            dummy = self.creator.staticText(_("LAMP Controller上に表示する名前を指定します。"))
        else: #更新時のメッセージ
            dummy = self.creator.staticText(_("LAMP Controllerのフォルダ情報を更新しています。"))
        self.name, dummy = self.creator.inputbox(_("名前"), x=700, textLayout=wx.HORIZONTAL)
        if self.nameValue != None:
            self.name.SetValue(self.nameValue)
            self.name.GetParent().Enable(False)
        self.processLabel = self.creator.staticText(_("ファイルを集めています..."), x=800)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bOk = self.creator.button("OK", self.onButtonClick)
        if self.nameValue != None: self.bOk.Enable(False)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"))

        self.makeFileList = makeFileListJson(self.path)
        self.makeFileList.start()

        self.timer = wx.Timer(self.wnd)
        self.wnd.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(2000)

    def GetData(self):
        return (self.name.GetValue(), self.path)
    
    def onTimer(self, evt):
        # 効果音
        if self.setName and self.makeFileList.pathList == None: fxManager.processing()
        
        # jsonができあがっていたら、もう集めていない
        if self.makeFileList.pathList != None: self.processLabel.SetLabel("")

        # 名前の設定が完了していて、JSON処理も終了していたときは送信
        if self.setName and self.makeFileList.pathList != None:
            self.bOk.Enable(False)
            self.bCancel.Enable(False)
            self.timer.Stop()
            self.sendJson()

    def onSendTimer(self, evt):
        fxManager.processing()
        val = self.sendProcess.returnValue
        if val == None: return
        self.sendTimer.Stop()
        self.processLabel.SetLabel("")
        if val == 200:
            self.success()
            self.Destroy()
            return
        elif val == "already entered":
            if self.confirmOverWrite(): return self.sendJson(True)
        elif val == "invalid name":
            self.error(_("フォルダ名は、1文字以上、30文字以内で指定してください。"))
        else:
            self.error(_("通信に失敗しました。ネットワーク接続などを確認してください。"))
        if self.nameValue != None:
            self.Destroy()
            return
        self.bOk.Enable()
        self.bCancel.Enable()
        self.setName = False
        self.timer.Start(1000)
        self.name.GetParent().Enable(True)
    
    def sendJson(self, overWrite=False):
        self.processLabel.SetLabel(_("通信中..."))
        self.sendProcess = sendJsonProcess()
        #更新処理の時は自動で上書き
        if self.nameValue == None: self.sendProcess.setValue(self.name.GetValue(), self.makeFileList, overWrite)
        else: self.sendProcess.setValue(self.name.GetValue(), self.makeFileList, True)
        self.sendProcess.start()
        self.sendTimer = wx.Timer()
        self.sendTimer.Bind(wx.EVT_TIMER, self.onSendTimer)
        self.sendTimer.Start(2000)

    def onButtonClick(self, event):
        evt = event.GetEventObject()
        if evt == self.bOk:
            netDirLower = []
            for k in globalVars.lampController.netDirDict:
                netDirLower.append(k.lower())
            if self.name.GetValue().lower() in netDirLower: return self.error(_("この名前は、すでに使用されています。"))
            self.bOk.Enable(False)
            self.setName = True
            self.name.GetParent().Enable(False)

    def success(self):
        d = mkDialog.Dialog("fileSendSuccess")
        d.Initialize(_("送信完了"), _("フォルダ情報の転送が完了しました。"), ["OK"], False)
        fxManager.confirm()
        d.Show()

    def confirmOverWrite(self):
        d = mkDialog.Dialog("fileSendOverWrite")
        d.Initialize(_("上書き確認"), _("このフォルダはすでに登録されています。上書きしますか。"), [_("はい(&Y)"), _("いいえ(&N)")], False)
        fxManager.confirm()
        if d.Show() == 0: return True
        else: return False
 

    def error(self, message):
        d = mkDialog.Dialog("netFileError")
        d.Initialize(_("エラー"), message, ["OK"], False)
        fxManager.error()
        d.Show()



# 単純ファイル情報追加ビュー
class netFileAddDialog(BaseDialog):
    def Initialize(self):
        self.title = _("フォルダの追加")
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,self.title)
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
        dummy = self.creator.staticText(_("フォルダの場所と、LAMP Controller上の名前を指定します。"))
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20, style=wx.ALL, margin=20)
        self.path, dummy = self.creator.inputbox(_("場所"), x=700, textLayout=wx.HORIZONTAL)
        self.bBrowse = self.creator.button(_("参照"), self.onButtonClick)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20, style=wx.ALL, margin=20)
        self.name, dummy = self.creator.inputbox(_("名前"), x=700, textLayout=wx.HORIZONTAL)
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
        self.bOk = self.creator.button("OK", self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"))

    def onButtonClick(self, evt):
        eo = evt.GetEventObject()
        if eo == self.bBrowse:
            d = wx.DirDialog(self.wnd)
            if d.ShowModal() == wx.ID_CANCEL: return
            else: self.path.SetValue(d.GetPath())
        elif eo == self.bOk:
            netDirLower = []
            for k in globalVars.lampController.netDirDict:
                netDirLower.append(k.lower())
            if self.name.GetValue().lower() in netDirLower:
                d = mkDialog.Dialog("alreadyEnteredError")
                d.Initialize(_("エラー"), _("この名前は、すでに使用されています。"), ["OK"], False)
                fxManager.error()
                d.Show()
            elif not os.path.exists(self.path.GetValue()):
                d = mkDialog.Dialog("pathNotFoundError")
                d.Initialize(_("エラー"), _("指定された場所が存在しません。"), ["OK"], False)
                fxManager.error()
                d.Show()
            else: self.Destroy()

    def GetData(self):
        return (self.name.GetValue(), self.path.GetValue())

class makeFileListJson(threading.Thread):
    def __init__(self, path):
        self.path = path
        self.pathList = None
        self.log=getLogger("%s.NetFileManager" % (constants.LOG_PREFIX,))
        super().__init__()

    def run(self):
        self.pathList = self.path2list(self.path)
        return

    def path2list(self, path):
        l = []
        ld = os.listdir(path)
        for s in ld:
            if os.path.isdir(os.path.join(path, s)):
                l.append({s: self.path2list(os.path.join(path, s))})
            else:
                l.append(s)
        return l

class sendJsonProcess(threading.Thread):
    def setValue(self, name, makeFileList, overWrite=False):
        self.log=getLogger("%s.NetFileManager" % (constants.LOG_PREFIX,))
        self.name = name
        self.makeFileList = makeFileList
        self.returnValue = None
        self.overWrite = overWrite

    def run(self):
        self.returnValue = self.sendJson(self.overWrite)

    def sendJson(self, overWrite=False):
        obj = {"file": [{self.name: self.makeFileList.pathList}], "apiVersion": constants.API_VERSION,
            "authentication": {"userName": globalVars.app.config.getstring("network", "user_name", ""), "softwareKey": globalVars.app.config.getstring("network", "software_key", "")},
            "software": {"driveSerialNo": win32api.GetVolumeInformation(os.environ["SystemRoot"][:3])[1], "pcName": os.environ["COMPUTERNAME"]},
            "overWrite": bool(overWrite)}
        try:
            rp = requests.post(constants.API_PUTFILE_URL, json=obj)
            rj = rp.json()
            if rj["code"] == 200:
                return 200
            elif (rj["code"] == 400 and rj["reason"] == "already entered") or (self.name.GetValue() in globalVars.lampController.netDirDict):
                return rj["reason"]
            elif rj["code"] == 400 and rj["reason"] == "invalid name":
                return rj["reason"]
                return False
            else:
                return "error"
        except Exception as e:
            self.log.error(str(e))
            return "error"

