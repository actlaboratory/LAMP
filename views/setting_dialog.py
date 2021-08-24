# setting dialog for LAMP
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx
import globalVars
import constants
from views import baseDialog, ViewCreator
from soundPlayer import player

class settingDialog(baseDialog.BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("環境設定"))
        self.readerDic = {
            "AUTO": _("自動選択"),
            "NVDA": "NVDA",
            "JAWS": "JAWS",
            "PCTK": "PC-Talker",
            "SAPI5": "SAPI5",
            "CLIPBOARD": _("クリップボード出力"),
            "NOSPEECH": _("読み上げなし")
        }
        self.fileInterruptDic = {
            "play": _("割り込み再生"),
            "addPlaylist": _("プレイリストに追加"),
            "addQueue": _("キューに追加"),
            "addQueueHead": _("キューの先頭に追加")
        }
        self.playlistInterruptDic = {
            "open": _("新たにプレイリストを開く"),
            "add": _("現在のプレイリストに追加")
        }
        self.startupPlayModeDic = {
            "normal": _("通常"),
            "repeat": _("リピート"),
            "loop": _("ループ"),
            "shuffle": _("シャッフル")
        }
        dl = player.getDeviceList()
        self.deviceDic = {}
        for i in range(len(dl)):
            if i == 0: self.deviceDic["default"] = _("規定の再生デバイス")
            elif dl[i] != None: self.deviceDic[dl[i]] = dl[i]
        self.notificationDeviceDic = {"same": _("音楽再生の出力先と同じ")}
        self.notificationDeviceDic.update(self.deviceDic)
        # 言語内容読み込み
        self.lang_code = list(constants.SUPPORTING_LANGUAGE.keys())
        self.lang_name = list(constants.SUPPORTING_LANGUAGE.values())
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        creator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20)

        # タブコントロール
        tabCtrl = creator.tabCtrl(_("環境設定"))

        # 一般
        generalCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("一般"), style=wx.ALL, margin=20)
        self.darkMode = generalCreator.checkbox(_("ダークモード（LAMPの再起動が必要）(&D)"))
        if globalVars.app.config.getstring("view", "colormode", "white", ("white", "dark")) == "white":
            self.darkMode.SetValue(False)
        else: self.darkMode.SetValue(True)
        self.langCombo,langLabel = generalCreator.combobox(_("言語（LAMPの再起動が必要）(&L)"), self.lang_name, textLayout=wx.HORIZONTAL)
        self.fadeOut = generalCreator.checkbox(_("終了時に曲をフェードアウトする(&C)"))
        if globalVars.app.config.getboolean("player", "fadeOutOnExit", False):
            self.fadeOut.SetValue(True)
        else: self.fadeOut.SetValue(False)
        self.manualFeed = generalCreator.checkbox(_("曲送りを手動で行う(&M)"))
        if globalVars.app.config.getboolean("player", "manualSongFeed", False):
            self.manualFeed.SetValue(True)
        else: self.manualFeed.SetValue(False)
        self.fileInterruptCombo, fileInterruptLabel = generalCreator.combobox(_("新たなファイルにより開かれたとき(&F)"), self.getValueList(self.fileInterruptDic), textLayout=wx.VERTICAL)
        self.playlistInterruptCombo, fileInterruptLabel = generalCreator.combobox(_("新たなプレイリストにより開かれたとき(&P)"), self.getValueList(self.playlistInterruptDic), textLayout=wx.VERTICAL)

        # 通知
        notificationCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("通知"), style=wx.ALL, margin=20)
        self.readerCombo, readerLabel = notificationCreator.combobox(_("音声読み上げの出力先(&S)"), self.getValueList(self.readerDic), textLayout=wx.HORIZONTAL)
        self.notificationSound = notificationCreator.checkbox(_("効果音による通知を有効にする(&I)"))
        if globalVars.app.config.getboolean("notification", "sound", True):
            self.notificationSound.SetValue(True)
        else: self.notificationSound.SetValue(False)
        self.notificationDeviceCombo, notificationDeviceLabel = notificationCreator.combobox(_("効果音出力先(&D)"), self.getValueList(self.notificationDeviceDic), textLayout=wx.HORIZONTAL)
        self.ignoreError = notificationCreator.checkbox(_("エラーを通知せず無視する(&E)"))
        if globalVars.app.config.getboolean("notification", "ignoreError", True):
            self.ignoreError.SetValue(True)
        else: self.ignoreError.SetValue(False)

        # 起動
        startupCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("起動"), style=wx.ALL, margin=20)
        self.volumeSlider, self.volumeLabel = startupCreator.slider(_("規定の音量(&V)"), 0, 100,None, globalVars.app.config.getint("volume","default",default=100, min=0, max=100), textLayout=wx.HORIZONTAL)
        self.startupDeviceCombo, startupDeviceLabel = startupCreator.combobox(_("起動時出力先(&D)"), self.getValueList(self.deviceDic), textLayout=wx.HORIZONTAL)
        self.startupListLabel = startupCreator.staticText(_("起動時に読み込むプレイリスト"))
        startupListCreator = ViewCreator.ViewCreator(self.viewMode, startupCreator.GetPanel(), startupCreator.GetSizer(), wx.HORIZONTAL,style=wx.EXPAND)
        self.startupList, dummy = startupListCreator.inputbox(_("起動時に読み込むプレイリスト(&P)"), defaultValue=globalVars.app.config.getstring("player", "startupPlaylist", ""), x=600, proportion=1,textLayout=None)
        self.startupList.hideScrollBar(wx.HORIZONTAL)
        self.startupListSelectBtn = startupListCreator.button(_("参照"), self.onButton)
        self.startupPlayModeCombo, self.startupPlayModeLabel = startupCreator.combobox(_("起動時再生モード(&M)"), self.getValueList(self.startupPlayModeDic), textLayout=wx.HORIZONTAL)

        # ネットワーク
        netCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("ネットワーク"), style=wx.ALL, margin=20)
        self.updateCheck = netCreator.checkbox(_("起動時に更新を確認(&U)"))
        if globalVars.app.config.getboolean("general", "update", True):
            self.updateCheck.SetValue(True)
        else: self.updateCheck.SetValue(False)
        self.manualProxy = netCreator.checkbox(_("手動でプロキシ設定を行う(&M)"), self.onCheckBox)
        if globalVars.app.config.getboolean("network", "manual_proxy", False):
            self.manualProxy.SetValue(True)
        else: self.manualProxy.SetValue(False)
        self.proxyServer, self.proxyServerLabel = netCreator.inputbox(_("サーバ名(&S)"), defaultValue=globalVars.app.config.getstring("network", "proxy_server", ""), x=400, textLayout=wx.HORIZONTAL)
        self.proxyServer.hideScrollBar(wx.HORIZONTAL)
        self.proxyPort, self.proxyPortLabel = netCreator.spinCtrl(_("ポート(&P)"), 0, 65535, None, globalVars.app.config.getint("network", "proxy_port", 8080, 0, 65535), textLayout=wx.HORIZONTAL)

        self.onCheckBox()

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, creator.GetSizer(), style=wx.ALIGN_RIGHT | wx.ALL, margin=10)
        self.saveBtn = footerCreator.button(_("保存"), self.onSaveButton)
        self.saveBtn.SetDefault()
        cancelBtn = footerCreator.cancelbutton(_("破棄"))

        self.comboloader()

    def onSaveButton(self, evt):
        if self.darkMode.IsChecked(): globalVars.app.config["view"]["colormode"] = "dark"
        else: globalVars.app.config["view"]["colormode"] = "white"
        globalVars.app.config["player"]["fadeOutOnExit"] = self.fadeOut.IsChecked()
        globalVars.app.config["player"]["manualSongFeed"] = self.manualFeed.IsChecked()
        globalVars.app.config["player"]["fileInterrupt"] = self.getKey(self.fileInterruptDic, self.fileInterruptCombo.GetStringSelection())
        globalVars.app.config["player"]["playlistInterrupt"] = self.getKey(self.playlistInterruptDic, self.playlistInterruptCombo.GetStringSelection())
        globalVars.app.config["speech"]["reader"] = self.getKey(self.readerDic, self.readerCombo.GetStringSelection())
        globalVars.app.config["notification"]["sound"] = self.notificationSound.IsChecked()
        globalVars.app.config["notification"]["outputDevice"] = self.getKey(self.notificationDeviceDic, self.notificationDeviceCombo.GetStringSelection())
        globalVars.app.config["notification"]["ignoreError"] = self.ignoreError.IsChecked()
        globalVars.app.config["volume"]["default"] = str(int(self.volumeSlider.GetValue()))
        globalVars.app.config["player"]["outputDevice"] = self.getKey(self.deviceDic, self.startupDeviceCombo.GetStringSelection())
        globalVars.app.config["player"]["startupPlaylist"] = self.startupList.GetValue()
        globalVars.app.config["player"]["startupPlayMode"] = self.getKey(self.startupPlayModeDic, self.startupPlayModeCombo.GetStringSelection())
        globalVars.app.config["general"]["language"] = self.lang_code[self.langCombo.GetSelection()]
        globalVars.app.config["general"]["update"] = self.updateCheck.IsChecked()
        globalVars.app.config["network"]["manual_proxy"] = self.manualProxy.IsChecked()
        globalVars.app.config["network"]["proxy_server"] = self.proxyServer.GetValue()
        globalVars.app.config["network"]["proxy_port"] = self.proxyPort.GetValue()

        # プロキシ即時反映
        if self.manualProxy.IsChecked():
            globalVars.app.proxyEnviron.set_environ(self.proxyServer.GetValue(), self.proxyPort.GetValue())
        else: globalVars.app.proxyEnviron.set_environ()
        

        self.wnd.EndModal(wx.ID_OK)

    def comboloader(self):
        fileInterrupt = globalVars.app.config.getstring("player", "fileInterrupt", "play", ("play", "addPlaylist", "addQueue", "addQueueHead"))
        selectionStr = self.fileInterruptDic[fileInterrupt]
        self.fileInterruptCombo.SetStringSelection(selectionStr)
        playlistInterrupt = globalVars.app.config.getstring("player", "playlistInterrupt", "open", ("open", "add"))
        selectionStr = self.playlistInterruptDic[playlistInterrupt]
        self.playlistInterruptCombo.SetStringSelection(selectionStr)
        reader = globalVars.app.config["speech"]["reader"]
        selectionStr = self.readerDic[reader]
        self.readerCombo.SetStringSelection(selectionStr)
        notificationDevice = globalVars.app.config.getstring("notification", "outputDevice", "default", self.getKeyList(self.notificationDeviceDic))
        selectionStr = self.notificationDeviceDic[notificationDevice]
        self.notificationDeviceCombo.SetStringSelection(selectionStr)
        startupDevice = globalVars.app.config.getstring("player", "outputDevice", "default", self.getKeyList(self.deviceDic))
        selectionStr = self.deviceDic[startupDevice]
        self.startupDeviceCombo.SetStringSelection(selectionStr)
        startupPlayMode = globalVars.app.config.getstring("player", "startupPlayMode", "normal", self.getKeyList(self.startupPlayModeDic))
        selectionStr = self.startupPlayModeDic[startupPlayMode]
        self.startupPlayModeCombo.SetStringSelection(selectionStr)
        language = globalVars.app.config.getstring("general", "language", "en_US", self.lang_code)
        selectionStr = constants.SUPPORTING_LANGUAGE[language]
        self.langCombo.SetStringSelection(selectionStr)

    def onCheckBox(self, evt=None):
        if evt == None: evtObject = None
        else: evtObject = evt.GetEventObject()
        if evtObject == self.manualProxy or evtObject == None:
            if self.manualProxy.IsChecked():
                self.proxyServer.GetParent().Enable()
                self.proxyPort.GetParent().Enable()
            else:
                self.proxyServer.GetParent().Disable()
                self.proxyPort.GetParent().Disable()

    def onButton(self, evt):
        if evt.GetEventObject() == self.startupListSelectBtn:
            fd = wx.FileDialog(None, _("プレイリストファイル選択"), wildcard=_("プレイリストファイル (.m3u8/.m3u)")+"|*.m3u8*;*.m3u")
            c = fd.ShowModal()
            if c == wx.ID_CANCEL: return
            path = fd.GetPath()
            self.startupList.SetValue(path)
    
    def getValueList(self, dic):
        ret = []
        for i in dic:
            ret.append(dic[i])
        return ret

    def getKeyList(self, dic):
        ret = []
        for k in dic:
            ret.append(k)
        return ret
    
    def getKey(self, dic, value):
        for i in dic:
            if dic[i] == value: return i
        return None

