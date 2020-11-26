# -*- coding: utf-8 -*-
# sleepTimer

from soundPlayer.constants import *
import wx
import os
from views import mkDialog

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("スリープタイマー設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL)
        # スリープの条件
        choice = [_("次の時間が経過した"), _("次の曲数を再生した"), _("キューの再生を完了した"), _("すべての再生が完了した")]
        self.conditionCombo, self.conditionLabel = self.creator.combobox(_("スリープの条件"), choice, self.onCombobox, 0, textLayout=wx.HORIZONTAL)
        #スリープの動作
        choice = [_("再生の停止"), _("LAMPの終了"), _("コンピュータをスリープ"),_("コンピュータの電源を切る")]
        self.motionCombo, self.motionLabel = self.creator.combobox(_("スリープの動作"), choice, self.onCombobox, 0, textLayout=wx.HORIZONTAL)
        #値の設定
        self.creator.AddSpace(20)
        self.timeValueCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.sizer,views.ViewCreator.wx.HORIZONTAL)
        timeLabel = self.timeValueCreator.staticText(_("時間と分の指定"))
        self.hourSpin, dummy = self.timeValueCreator.spinCtrl(_("時間"), 0, 24, self.onSpin, 0, textLayout=None)
        label = self.timeValueCreator.staticText(_("時間") + " ")
        self.minSpin, dummy = self.timeValueCreator.spinCtrl(_("分"), 0, 59, self.onSpin, 0, textLayout=None)
        label = self.timeValueCreator.staticText(_("分"))
        self.countValueCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.sizer,views.ViewCreator.wx.HORIZONTAL)
        countLabel = self.countValueCreator.staticText(_("曲数指定"))
        self.countSpin, dummy = self.countValueCreator.spinCtrl(_("曲数"), 0, 999, self.onSpin, 0, textLayout=None)
        label = self.countValueCreator.staticText(_("曲"))
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"", wx.ALIGN_RIGHT)
        self.bStart = self.creator.button(_("開始"),self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"), self.onButtonClick)

        self.sizer.Hide(self.countValueCreator.GetSizer(), True)
        self.panel.Layout()

    def onCombobox(self, evt):
        evtObj = evt.GetEventObject()
        if evtObj == self.conditionCombo:
            if evtObj.GetValue() == _("次の時間が経過した"):
                self.sizer.Show(self.timeValueCreator.GetSizer(), True, True)
                self.sizer.Hide(self.countValueCreator.GetSizer(), True)
                self.panel.Layout()
            elif evtObj.GetValue() == _("次の曲数を再生した"):
                self.sizer.Hide(self.timeValueCreator.GetSizer(), True)
                self.sizer.Show(self.countValueCreator.GetSizer(), True, True)
                self.panel.Layout()
            else:
                self.sizer.Hide(self.timeValueCreator.GetSizer(), True)
                self.sizer.Hide(self.countValueCreator.GetSizer(), True)


    def GetData(self):
        if self.conditionCombo.GetValue() == _("次の時間が経過した"):
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue(), self.hourSpin.GetValue(), self.minSpin.GetValue())
        elif self.conditionCombo.GetValue() == _("次の曲数を再生した"):
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue(), self.countSpin.GetValue())
        else:
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue())

    def onSpin(self, evt):
        return None

    def onButtonClick(self, evt):
        if evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)
        elif evt.GetEventObject()==self.bStart:
            if self.check(): self.wnd.EndModal(1)

    def check(self):
        #0分のタイマーは設定できない
        if self.GetData()[0] == _("次の時間が経過した") and self.GetData()[2] == 0 and self.GetData()[3] == 0:
            self.errorDialog(_("タイマーには１分以上の長さが必要です。"))
            return False
        #キューが消費済みであれば設定できない
        elif self.GetData()[0] == _("キューの再生を完了した") and len(globalVars.queue.lst) == 0:
            self.errorDialog(_("キューにアイテムがないため、このタイマーを設定できません。"))
            return False
        #再生するアイテムがなければ設定できない
        elif self.GetData()[0] == _("すべての再生が完了した") and len(globalVars.app.hMainView.playlistView.lst) == 0 and len(globalVars.queue.lst) == 0 and globalVars.play.getStatus() == PLAYER_STATUS_STOPPED:
            self.errorDialog(_("再生する曲がないため、このタイマーを設定できません。"))
            return False
        worning = [] #警告の処理
        if (self.GetData()[0] == _("次の曲数を再生した") or self.GetData()[0] == _("すべての再生が完了した")) and globalVars.eventProcess.shuffleCtrl != None:
            worning.append(_("シャッフルが有効です。"))
        if globalVars.eventProcess.repeatLoopFlag == 2:
            worning.append(_("ループが有効です。"))
        if self.GetData()[0] != _("次の時間が経過した") and globalVars.eventProcess.repeatLoopFlag == 1:
            worning.append(_("リピートが有効です。"))
        if len(worning) == 0: return True
        else:
            self.worningDialog(_("以下の理由により、このままではタイマーが終了しません。")+"\n"*2+"\n".join(worning))
            return True

    def errorDialog(self, message):
        d = mkDialog.Dialog("sleepTimerErrorDialog")
        d.Initialize(_("エラー"), message, (_("やり直す"),))
        d.Show()

    def worningDialog(self, message):
        d = mkDialog.Dialog("sleepTimerWorningDialog")
        d.Initialize(_("お知らせ"), message, (_("了解"),))
        d.Show()
