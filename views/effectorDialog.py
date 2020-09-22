# -*- coding: utf-8 -*-
# effector

import wx
import os
import globalVars
import views.ViewCreator
from views import mkDialog
from soundPlayer.constants import *

import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("エフェクト設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        # 増幅設定
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.ampSlider, dummy = self.creator.slider(_("増幅"), 0, 400, self.onSlider, globalVars.play.getConfig(PLAYER_CONFIG_AMP), x=150)
        self.ampSpin, dummy = self.creator.spinCtrl(_("増幅"), 0, 400, self.onSpin, globalVars.play.getConfig(PLAYER_CONFIG_AMP), textLayout=None)
        # 速さ設定
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.tempoSlider, dummy = self.creator.slider(_("速さ"),15, 500,self.onSlider, globalVars.play.getConfig(PLAYER_CONFIG_SPEED), x=150)
        self.tempoSpin, dummy = self.creator.spinCtrl(_("速さ"), 15, 500, self.onSpin, globalVars.play.getConfig(PLAYER_CONFIG_SPEED), textLayout=None)
        # ピッチ変更
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.pitchSlider, dummy = self.creator.slider(_("キー"), -60, 60, self.onSlider, globalVars.play.getConfig(PLAYER_CONFIG_KEY), x=150)
        self.pitchSpin, dummy = self.creator.spinCtrl(_("キー"), -60, 60, self.onSpin, globalVars.play.getConfig(PLAYER_CONFIG_KEY), textLayout=None)
        # 周波数変更
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.freqSlider, dummy = self.creator.slider(_("周波数"), 6, 400, self.onSlider, globalVars.play.getConfig(PLAYER_CONFIG_FREQ), x=150)
        self.freqSpin, dummy = self.creator.spinCtrl(_("周波数"), 6, 400, self.onSpin, globalVars.play.getConfig(PLAYER_CONFIG_FREQ), textLayout=None)
        # フッタ
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"", wx.ALIGN_RIGHT)
        self.bClose = self.creator.button(_("閉じる"),self.onButtonClick)
        self.bReset = self.creator.button(_("リセット"), self.onButtonClick)

    def GetData(self):
        return (self.ampSlider.GetValidator(), self.tempoSlider.GetValue(), self.pitchSlider.GetValue(), self.freqSlider.GetValue())

    def onSpin(self, evt):
        obj = evt.GetEventObject()
        if obj == self.ampSpin:
            self.ampSlider.SetValue(obj.GetValue())
            globalVars.play.setAmp(obj.GetValue())
        elif obj == self.tempoSpin:
            self.tempoSlider.SetValue(obj.GetValue())
            globalVars.play.setSpeed(obj.GetValue())
        elif obj == self.pitchSpin:
            self.pitchSlider.SetValue(obj.GetValue())
            globalVars.play.setKey(obj.GetValue())
        elif obj == self.freqSpin:
            self.freqSlider.SetValue(obj.GetValue())
            globalVars.play.setFreq(obj.GetValue())


    def onSlider(self, evt):
        obj = evt.GetEventObject()
        if obj == self.ampSlider:
            self.ampSpin.SetValue(obj.GetValue())
            globalVars.play.setAmp(obj.GetValue())
        elif obj == self.tempoSlider:
            self.tempoSpin.SetValue(obj.GetValue())
            globalVars.play.setSpeed(obj.GetValue())
        elif obj == self.pitchSlider:
            self.pitchSpin.SetValue(obj.GetValue())
            globalVars.play.setKey(obj.GetValue())
        elif obj == self.freqSlider:
            self.freqSpin.SetValue(obj.GetValue())
            globalVars.play.setFreq(obj.GetValue())

    def onButtonClick(self, evt):
        if evt.GetEventObject()==self.bClose:
            self.wnd.EndModal(1)
        elif evt.GetEventObject()==self.bReset:
            
            self.ampSlider.SetValue(100)
            self.ampSpin.SetValue(100)
            globalVars.play.setAmp(100)
            self.tempoSlider.SetValue(100)
            self.tempoSpin.SetValue(100)
            globalVars.play.setSpeed(100)
            self.pitchSlider.SetValue(0)
            self.pitchSpin.SetValue(0)
            globalVars.play.setKey(0)
            self.freqSlider.SetValue(100)
            self.freqSpin.SetValue(100)
            globalVars.play.setFreq(100)
