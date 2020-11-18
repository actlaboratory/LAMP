import wx
import globalVars, fileAssocUtil
from views import baseDialog, ViewCreator, mkDialog
from soundPlayer import player

UNSET = 1001

def assocDialog():
    d = dialog("fileAssocDialoa")
    d.Initialize()
    r = d.Show()
    if r == wx.ID_OK:
        l = d.GetValue()
        for s in l:
            if not fileAssocUtil.setAssoc(s, "lamp.audio"):
                e = mkDialog.Dialog("fileAssocError")
                e.Initialize(_("エラー"), _("拡張子関連付け情報の書き込みに失敗しました。"), ("了解",))
                e.Show()
                break
    elif r == UNSET: fileAssocUtil.unsetAssoc("lamp.audio")

class dialog(baseDialog.BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("環境設定"))
        self.checkBoxs = {}
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        cbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, ViewCreator.GridSizer, 20, 3)

        for s in globalVars.fileExpansions:
            self.checkBoxs[s.lower()] = cbCreator.checkbox(s[1:].upper())

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer)
        self.okBtn = footerCreator.okbutton(_("登録"))
        cancelBtn = footerCreator.cancelbutton(_("中止"))
        unsetBtn = footerCreator.button(_("全関連付けを解除"), self.onUnsetBtn)


    def onUnsetBtn(self, evt):
        self.wnd.EndModal(UNSET)

    def GetData(self):
        l = []
        for k in self.checkBoxs:
            if self.checkBoxs[k].IsChecked(): l.append(k.lower())
        return l
