# -*- coding: utf-8 -*-
# sleepTimer

import wx
import os

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self):
        self.identifier=_("スリープタイマー設定") #このビューを表す文字列
        self.log=getLogger(self.identifier)
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("スリープタイマー設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,views.ViewCreator.GridSizer,2)
        # スリープの条件
        choice = [_("次の時間が経過した"), _("次の局数を再生した"), _("キューの再生を完了した"), _("すべての再生が完了した")]
        self.conditionLabel, self.conditionCombo = self.creator.combobox(_("スリープの条件"), choice, self.onCombobox, 0)
        choice = [_("再生の停止"), _("LAMPの終了"), _("電源を切る")]
        self.motionLabel, self.motionCombo = self.creator.combobox(_("スリープの動作"), choice, self.onCombobox, 0)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self.bStart = self.creator.button(_("開始"),self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"), self.onButtonClick)

    def onCombobox(self, evt):
        return None

    def GetData(self):
        return "テスト"

    def onButtonClick(self, evt):
        if evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)
        elif evt.GetEventObject()==self.bStart: self.wnd.EndModal(1)
        