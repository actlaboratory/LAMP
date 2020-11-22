# versionDialog
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx
import constants
from views import baseDialog, ViewCreator, mkDialog


def versionDialog():
    d = dialog("versionInfoDialoa")
    d.Initialize()
    d.Show()


class dialog(baseDialog.BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("バージョン情報"))
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        versionCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 10)
        textList = []
        textList.append(str(constants.APP_FULL_NAME) + " (" + constants.APP_NAME + ")")
        textList.append(_("ソフトウェアバージョン") + ": " + str(constants.APP_VERSION))
        textList.append(_("アップデータバージョン") + ": " + "---")
        textList.append(_("ライセンス") + ": " + constants.APP_LICENSE)
        textList.append(_("開発元") + ": %s - %s" %(constants.APP_DEVELOPERS, constants.APP_DEVELOPERS_URL))
        textList.append(_("ソフトウェア詳細情報") + ": " + constants.APP_DETAILS_URL)
        textList.append("")
        textList.append(_("本ソフトウェアには、他の団体または個人の成果物が含まれている場合があります。ライセンス情報の詳細については,同梱の license.txt を参照してくださtい。"))
        textList.append("")
        textList.append("Copyright (c) %s %s All lights reserved." %(constants.APP_COPYRIGHT_YEAR, constants.APP_DEVELOPERS))

        self.info, dummy = versionCreator.inputbox("", defaultValue="\r\n".join(textList), style=wx.TE_MULTILINE|wx.TE_READONLY, sizerFlag=wx.EXPAND, x=750, textLayout=None)

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, style=wx.ALIGN_RIGHT)
        self.closeBtn = footerCreator.cancelbutton(_("閉じる"))
        self.closeBtn.SetDefault()


    def onUnsetBtn(self, evt):
        self.wnd.EndModal(UNSET)

    def GetData(self):
        l = []
        for k in self.checkBoxs:
            if self.checkBoxs[k].IsChecked(): l.append(k.lower())
        return l
