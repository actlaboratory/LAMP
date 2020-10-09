import wx
import globalVars
from views import baseDialog, ViewCreator

class settingDialog(baseDialog.BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("環境設定"))
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

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, creator.GetSizer())
        self.saveBtn = footerCreator.button(_("保存"), self.onSaveButton)
        cancelBtn = footerCreator.cancelbutton(_("破棄"))

    def onSaveButton(self, evt):
        if self.darkMode.IsChecked(): globalVars.app.config["view"]["colormode"] = "dark"
        else: globalVars.app.config["view"]["colormode"] = "white"
        globalVars.app.config["volume"]["default"] = str(int(self.volumeSlider.GetValue()))
        self.wnd.EndModal(wx.ID_OK)