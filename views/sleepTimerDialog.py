# -*- coding: utf-8 -*-
# sleepTimer

from soundPlayer.constants import *
import wx
import os
import globalVars
from views import mkDialog

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def __init__(self, *pArg, **kArg):
        super().__init__(*pArg, **kArg)
        self.TIME_COUNTER = _("指定の時間が経過した")
        self.PLAY_COUNTER = _("指定の曲数を再生した")
        self.PLAY_END = _("すべての再生を完了した")
        self.QUQUQ_END = _("キューの再生が完了した")
        self.DO_STOP = _("再生の停止")
        self.DO_EXIT = _("LAMPの終了")
        self.DO_SLEEP = _("コンピュータのスリープ")
        self.DO_SHUTDOWN = _("コンピュータの電源を切る")

    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("スリープタイマー設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL, style=wx.ALL, margin=20)
        # スリープの条件
        choice = [self.TIME_COUNTER, self.PLAY_COUNTER,self.QUQUQ_END, self.PLAY_END]
        self.conditionCombo, self.conditionLabel = self.creator.combobox(_("スリープの条件"), choice, self.onCombobox, 0, textLayout=wx.HORIZONTAL)
        #スリープの動作
        choice = [self.DO_STOP, self.DO_EXIT, self.DO_SLEEP,self.DO_SHUTDOWN]
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
            if evtObj.GetValue() == self.TIME_COUNTER:
                self.sizer.Show(self.timeValueCreator.GetSizer(), True, True)
                self.sizer.Hide(self.countValueCreator.GetSizer(), True)
                self.panel.Layout()
            elif evtObj.GetValue() == self.PLAY_COUNTER:
                self.sizer.Hide(self.timeValueCreator.GetSizer(), True)
                self.sizer.Show(self.countValueCreator.GetSizer(), True, True)
                self.panel.Layout()
            else:
                self.sizer.Hide(self.timeValueCreator.GetSizer(), True)
                self.sizer.Hide(self.countValueCreator.GetSizer(), True)


    def GetData(self):
        if self.conditionCombo.GetValue() == self.TIME_COUNTER:
            return (self.conditionCombo.GetValue(), self.motionCombo.GetValue(), self.hourSpin.GetValue(), self.minSpin.GetValue())
        elif self.conditionCombo.GetValue() == self.PLAY_COUNTER:
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
        if self.GetData()[0] == self.TIME_COUNTER and self.GetData()[2] == 0 and self.GetData()[3] == 0:
            self.errorDialog(_("タイマーには１分以上の長さが必要です。"))
            return False
        #キューが消費済みであれば設定できない
        elif self.GetData()[0] == self.QUQUQ_END and len(globalVars.queue.lst) == 0:
            self.errorDialog(_("キューにアイテムがないため、このタイマーを設定できません。"))
            return False
        #再生するアイテムがなければ設定できない
        elif self.GetData()[0] == self.PLAY_END and len(globalVars.app.hMainView.playlistView.lst) == 0 and len(globalVars.queue.lst) == 0 and globalVars.play.getStatus() == PLAYER_STATUS_STOPPED:
            self.errorDialog(_("再生する曲がないため、このタイマーを設定できません。"))
            return False
        worning = [] #警告の処理
        if (self.GetData()[0] == self.PLAY_COUNTER or self.GetData()[0] == self.PLAY_END) and globalVars.eventProcess.shuffleCtrl != None:
            worning.append(_("シャッフルが有効です。"))
        if globalVars.eventProcess.repeatLoopFlag == 2:
            worning.append(_("ループが有効です。"))
        if self.GetData()[0] != self.TIME_COUNTER and globalVars.eventProcess.repeatLoopFlag == 1:
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
