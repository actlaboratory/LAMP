import wx
import globalVars, fileAssocUtil, fxManager
from views import baseDialog, ViewCreator, mkDialog, mkDialog
from soundPlayer import player

UNSET = 1001

def assocDialog():
    d = dialog("fileAssocDialog")
    d.Initialize()
    r = d.Show()
    if r == wx.ID_OK:
        l = d.GetValue()
        for s in l:
            if not fileAssocUtil.setAssoc(s, "lamp.audio"):
                e = mkDialog.Dialog("fileAssocError")
                e.Initialize(_("エラー"), _("ファイル関連付け情報の書き込みに失敗しました。"), ("了解",))
                fxManager.error()
                e.Show()
                break
            nd = mkDialog.Dialog("fileAssocOk")
            nd.Initialize(_("拡張子関連付け完了"), _("ファイルの関連付け情報を書き込みました。\r\nファイルのコンテキストメニュー内、\r\n[プログラムから開く] > [別のプログラムを選択]\r\nに表示されます。"), ("了解",))
            nd.Show()
    elif r == UNSET:
        if fileAssocUtil.unsetAssoc("lamp.audio"):
            nd = mkDialog.Dialog("unsetFileAssocOk")
            nd.Initialize(_("関連付け解除完了"), _("ファイルの関連付けを解除しました。"), ("OK",))
            nd.Show()
        else:
            e = mkDialog.Dialog("unsetFileAssocError")
            e.Initialize(_("エラー"), _("ファイルの関連付けを解除できませんでした。"), ("OK",))
            fxManager.error()
            e.Show()

class dialog(baseDialog.BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("拡張子関連付け設定"))
        self.checkBoxs = {}
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        lbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20, style = wx.ALL, margin=20)
        topLb = lbCreator.staticText(_("規定のアプリとして登録したいファイル形式に\nチェックを入れ、登録ボタンを選択します。\n解除するには、全関連付け解除を選択します。"))
        
        cbLbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20, _("音声ファイル"), style=wx.ALL | wx.EXPAND, margin=20)
        cbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, cbLbCreator.GetSizer(), ViewCreator.GridSizer, 20, 4, style=wx.EXPAND)
        for s in globalVars.fileExpansions:
            self.checkBoxs[s.lower()] = cbCreator.checkbox(s[1:].upper(), sizerFlag=wx.ALIGN_CENTER)

        m3uLbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 20, _("プレイリストファイル"), style=wx.ALL | wx.EXPAND, margin = 20)
        m3uCbCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, m3uLbCreator.GetSizer(), ViewCreator.GridSizer, 20, 4, style=wx.EXPAND)
        self.checkBoxs[".m3u"] = m3uCbCreator.checkbox("M3U", sizerFlag=wx.ALIGN_CENTER)
        self.checkBoxs[".m3u8"] = m3uCbCreator.checkbox("M3U8", sizerFlag=wx.ALIGN_CENTER)
        
        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, style=wx.ALL | wx.ALIGN_RIGHT, margin=20)
        self.okBtn = footerCreator.okbutton(_("登録"), self.onOkBtn)
        cancelBtn = footerCreator.cancelbutton(_("中止"))
        unsetBtn = footerCreator.button(_("全関連付け解除"), self.onUnsetBtn)


    def onOkBtn(self, evt):
        if len(self.GetData()) == 0:
            d = mkDialog.Dialog("fileType_notSelected")
            d.Initialize(_("エラー"), _("1つ以上のファイル形式を選択してください。"), ("OK",))
            fxManager.error()
            d.Show()

        else: self.wnd.EndModal(wx.ID_OK)

    def onUnsetBtn(self, evt):
        self.wnd.EndModal(UNSET)

    def GetData(self):
        l = []
        for k in self.checkBoxs:
            if self.checkBoxs[k].IsChecked(): l.append(k.lower())
        return l
