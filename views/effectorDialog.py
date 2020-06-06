# -*- coding: utf-8 -*-
# effector

import wx
import os
import globalVars
import views.ViewCreator
from views import mkDialog

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self):
        self.identifier=_("エフェクト設定") #このビューを表す文字列
        self.log=getLogger(self.identifier)
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("エフェクト設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        # 速さ設定
        self.tempoLabel = self.creator.staticText(_("速さ"),0)
        self.tempoSlider = self.creator.slider(_("速さ"),150, globalVars.play.channelTempo, 5000, 5)
        self.tempoSlider.Bind(wx.EVT_COMMAND_SCROLL, self.onSlider)
        self.tempoSpin = self.creator.SpinCtrl(0, 5000, globalVars.play.channelTempo, self.onSpin)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"", wx.ALIGN_RIGHT)
        self.bConfirm = self.creator.button(_("決定"),self.onButtonClick)
        self.bCancel = self.creator.cancelbutton(_("キャンセル"), self.onButtonClick)

    def GetData(self):
        return self.tempoSlider.GetValue()

    def onSpin(self, evt):
        obj = evt.GetEventObject()
        if obj == self.tempoSpin:
            self.tempoSlider.SetValue(obj.GetValue())

    def onSlider(self, evt):
        obj = evt.GetEventObject()
        if obj == self.tempoSlider:
            self.tempoSpin.SetValue(obj.GetValue())

    def onButtonClick(self, evt):
        if evt.GetEventObject() == self.bCancel: self.wnd.EndModal(wx.ID_CANCEL)
        elif evt.GetEventObject()==self.bOk:
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
        elif self.GetData()[0] == _("すべての再生が完了した") and len(globalVars.playlist.lst) == 0 and len(globalVars.queue.lst) == 0 and globalVars.play.getChannelState() == player.state.COLD:
            self.errorDialog(_("再生する曲がないため、このタイマーを設定できません。"))
            return False
        worning = [] #警告の処理
        if (self.GetData()[0] == _("次の曲数を再生した") or self.GetData()[0] == _("すべての再生が完了した")) and globalVars.eventProcess.shuffleCtrl != 0:
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
        d = mkDialog.Dialog()
        d.Initialize(_("エラー"), message, (_("やり直す"),))
        d.Show()

    def worningDialog(self, message):
        d = mkDialog.Dialog()
        d.Initialize(_("お知らせ"), message, (_("了解"),))
        d.Show()
