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
        super().Initialize(self.app.hMainView.hFrame,_("拡張子関連付け設定"))
        self.checkBoxs = {}
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        lbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20)
        topLb = lbCreator.staticText(_("規定のアプリとして登録したいファイル形式に\nチェックを入れ、登録ボタンを選択します。\n解除するには、全関連付け解除を選択します。"))
        
        cbLbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20)
        label = cbLbCreator.staticText(_("音声ファイル"))
        cbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, ViewCreator.GridSizer, 20, 3)
        for s in globalVars.fileExpansions:
            self.checkBoxs[s.lower()] = cbCreator.checkbox(s[1:].upper())

        m3uLbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20)
        m3uLabel = m3uLbCreator.staticText(_("プレイリストファイル"))
        m3uCbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, ViewCreator.GridSizer, 20, 3)
        self.checkBoxs[".m3u"] = m3uCbCreator.checkbox("M3U")
        self.checkBoxs[".m3u8"] = m3uCbCreator.checkbox("M3U8")
        
        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer)
        self.okBtn = footerCreator.okbutton(_("登録"))
        cancelBtn = footerCreator.cancelbutton(_("中止"))
        unsetBtn = footerCreator.button(_("全関連付け解除"), self.onUnsetBtn)


    def onUnsetBtn(self, evt):
        self.wnd.EndModal(UNSET)

    def GetData(self):
        l = []
        for k in self.checkBoxs:
            if self.checkBoxs[k].IsChecked(): l.append(k.lower())
        return l
