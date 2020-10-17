import wx
import globalVars
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
        dl = player.getDeviceList()
        self.deviceDic = {}
        for i in range(len(dl)):
            if i == 0: self.deviceDic["default"] = _("規定の再生デバイス")
            elif dl[i] != None: self.deviceDic[dl[i]] = dl[i]
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        creator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20)

        # タブコントロール
        tabCtrl = creator.tabCtrl(_("環境設定"))

        # 一般
        generalCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("一般"))
        self.darkMode = generalCreator.checkbox(_("ダークモード（白黒反転）"))
        if globalVars.app.config.getstring("view", "colormode", "white", ("white", "dark")) == "white":
            self.darkMode.SetValue(False)
        else: self.darkMode.SetValue(True)
        self.volumeSlider, self.volumeLabel = generalCreator.slider(_("規定の音量"), 0, 100,None, globalVars.app.config.getint("volume","default",default=100, min=0, max=100), textLayout=wx.HORIZONTAL)
        self.fadeOut = generalCreator.checkbox(_("終了時に曲をフェードアウトする"))
        if globalVars.app.config.getboolean("player", "fadeOutOnExit", False):
            self.fadeOut.SetValue(True)
        else: self.fadeOut.SetValue(False)
        self.fileInterruptCombo, fileInterruptLabel = generalCreator.combobox(_("ファイル割り込み時の操作"), self.getValueList(self.fileInterruptDic), textLayout=wx.HORIZONTAL)
        self.manualFeed = generalCreator.checkbox(_("曲送りを手動で行う"))
        if globalVars.app.config.getboolean("player", "manualSongFeed", False):
            self.manualFeed.SetValue(True)
        else: self.manualFeed.SetValue(False)

        # 通知
        notificationCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("通知"))
        self.readerCombo, readerLabel = notificationCreator.combobox(_("音声読み上げの出力先"), self.getValueList(self.readerDic), textLayout=wx.HORIZONTAL)
        self.notificationSound = notificationCreator.checkbox(_("効果音による通知を有効にする"))
        if globalVars.app.config.getboolean("notification", "sound", True):
            self.notificationSound.SetValue(True)
        else: self.notificationSound.SetValue(False)
        self.notificationDeviceCombo, notificationDeviceLabel = notificationCreator.combobox(_("効果音出力先"), self.getValueList(self.deviceDic), textLayout=wx.HORIZONTAL)

        # 起動
        startupCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("起動"))
        self.startupDeviceCombo, startupDeviceLabel = startupCreator.combobox(_("起動時出力先"), self.getValueList(self.deviceDic), textLayout=wx.HORIZONTAL)
        self.startupList, startupListLabel = startupCreator.inputbox(_("起動時に読み込むプレイリスト"), defaultValue=globalVars.app.config.getstring("player", "startupPlaylist", ""), x=-1)

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, creator.GetSizer())
        self.saveBtn = footerCreator.button(_("保存"), self.onSaveButton)
        cancelBtn = footerCreator.cancelbutton(_("破棄"))

        self.comboloader()

    def onSaveButton(self, evt):
        if self.darkMode.IsChecked(): globalVars.app.config["view"]["colormode"] = "dark"
        else: globalVars.app.config["view"]["colormode"] = "white"
        globalVars.app.config["volume"]["default"] = str(int(self.volumeSlider.GetValue()))
        globalVars.app.config["player"]["fadeOutOnExit"] = self.fadeOut.IsChecked()
        globalVars.app.config["player"]["fileInterrupt"] = self.getKey(self.fileInterruptDic, self.fileInterruptCombo.GetStringSelection())
        globalVars.app.config["player"]["manualSongFeed"] = self.manualFeed.IsChecked()
        globalVars.app.config["speech"]["reader"] = self.getKey(self.readerDic, self.readerCombo.GetStringSelection())
        globalVars.app.config["notification"]["sound"] = self.notificationSound.IsChecked()
        globalVars.app.config["notification"]["outputDevice"] = self.getKey(self.deviceDic, self.notificationDeviceCombo.GetStringSelection())
        globalVars.app.config["player"]["outputDevice"] = self.getKey(self.deviceDic, self.startupDeviceCombo.GetStringSelection())
        globalVars.app.config["player"]["startupPlaylist"] = self.startupList.GetValue()
        self.wnd.EndModal(wx.ID_OK)

    def comboloader(self):
        fileInterrupt = globalVars.app.config.getstring("player", "fileInterrupt", "play", ("play", "addPlaylist", "addQueue", "addQueueHead"))
        selectionStr = self.fileInterruptDic[fileInterrupt]
        self.fileInterruptCombo.SetStringSelection(selectionStr)
        reader = globalVars.app.config["speech"]["reader"]
        selectionStr = self.readerDic[reader]
        self.readerCombo.SetStringSelection(selectionStr)
        notificationDevice = globalVars.app.config.getstring("notification", "outputDevice", "default", self.getKeyList(self.deviceDic))
        selectionStr = self.deviceDic[notificationDevice]
        self.notificationDeviceCombo.SetStringSelection(selectionStr)
        startupDevice = globalVars.app.config.getstring("player", "outputDevice", "default", self.getKeyList(self.deviceDic))
        selectionStr = self.deviceDic[startupDevice]
        self.startupDeviceCombo.SetStringSelection(selectionStr)

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

