import wx
import globalVars
from views import baseDialog, ViewCreator

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

        # 通知
        notificationCreator = ViewCreator.ViewCreator(self.viewMode, tabCtrl, None, wx.VERTICAL, label=_("通知"))
        self.readerCombo, readerLabel = notificationCreator.combobox(_("音声読み上げの出力先"), self.getValueList(self.readerDic))

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, creator.GetSizer())
        self.saveBtn = footerCreator.button(_("保存"), self.onSaveButton)
        cancelBtn = footerCreator.cancelbutton(_("破棄"))

        self.comboloader()

    def onSaveButton(self, evt):
        if self.darkMode.IsChecked(): globalVars.app.config["view"]["colormode"] = "dark"
        else: globalVars.app.config["view"]["colormode"] = "white"
        globalVars.app.config["volume"]["default"] = str(int(self.volumeSlider.GetValue()))
        globalVars.app.config["speech"]["reader"] = self.getKey(self.readerDic, self.readerCombo.GetStringSelection())
        self.wnd.EndModal(wx.ID_OK)

    def comboloader(self):
        reader = globalVars.app.config["speech"]["reader"]
        selectionStr = self.readerDic[reader]
        self.readerCombo.SetStringSelection(selectionStr)

    def getValueList(self, dic):
        ret = []
        for i in dic:
            ret.append(dic[i])
        return ret

    def getKey(self, dic, value):
        for i in dic:
            if dic[i] == value: return i
        return None

