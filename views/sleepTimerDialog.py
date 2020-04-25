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
        choice = [_("次の時間が経過した"), _("次の曲数を再生した"), _("キューの再生を完了した"), _("すべての再生が完了した")]
        self.conditionLabel, self.conditionCombo = self.creator.combobox(_("スリープの条件"), choice, self.onCombobox, 0)
        #スリープの動作
        choice = [_("再生の停止"), _("LAMPの終了"), _("コンピュータをスリープ"),_("コンピュータの電源を切る")]
        self.motionLabel, self.motionCombo = self.creator.combobox(_("スリープの動作"), choice, self.onCombobox, 0)
        #値の設定
        self.valueLabel = self.creator.staticText(_("時間と分の指定"))
        self.valueCreator=views.ViewCreator.ViewCreator(1,self.panel,self.creator.sizer,views.ViewCreator.wx.HORIZONTAL)
        self.value1Spin = self.valueCreator.SpinCtrl(0, 24, 0, self.onSpin)
        self.value1Label = self.valueCreator.staticText(" : ")
        self.value2Spin = self.valueCreator.SpinCtrl(0, 59, 0, self.onSpin)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"", wx.ALIGN_RIGHT)
        self.bStart = self.creator.button(_("開始"),self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"), self.onButtonClick)

    def onCombobox(self, evt):
        evtObj = evt.GetEventObject()
        if evtObj == self.conditionCombo:
            if evtObj.GetValue() == _("次の時間が経過した"):
                self.valueLabel.SetLabel(_("時間と分の指定"))
                self.valueLabel.Show()
                self.value1Spin.SetMax(24)
                self.value1Spin.SetValue(0)
                self.value1Spin.Show()
                self.value1Label.SetLabel(" : ")
                self.value1Label.Show()
                self.value2Spin.SetMax(59)
                self.value2Spin.Show()
            elif evtObj.GetValue() == _("次の曲数を再生した"):
                self.valueLabel.SetLabel(_("曲数の指定"))
                self.valueLabel.Show()
                self.value1Spin.SetMax(999)
                self.value1Spin.SetValue(0)
                self.value1Spin.Show()
                self.value1Label.SetLabel(_("曲"))
                self.value1Label.Show()
                self.value2Spin.Show(False)
            else:
                self.valueLabel.Show(False)
                self.value1Spin.Show(False)
                self.value1Label.Show(False)
                self.value2Spin.Show(False)



    def GetData(self):
        if self.conditionCombo.GetValue() == _("次の時間が経過した"):
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue(), self.value1Spin.GetValue(), self.value2Spin.GetValue())
        elif self.conditionCombo.GetValue() == _("次の曲数を再生した"):
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue(), self.value1Spin.GetValue())
        else:
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue())

    def onSpin(self, evt):
        return None

    def onButtonClick(self, evt):
        if evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)
        elif evt.GetEventObject()==self.bStart: self.wnd.EndModal(1)
