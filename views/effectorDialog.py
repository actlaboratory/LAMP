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
        
        # 定数
        self.TEMPO = 0
        self.PITCH = 1
        self.FREQ = 2

        super().Initialize(self.app.hMainView.hFrame,_("エフェクト設定"))
        self.InstallControls()

        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        # 速さ設定
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.tempoLabel = self.creator.staticText(_("速さ"),0)
        self.tempoSlider = self.creator.slider(_("速さ"),150, globalVars.play.channelTempo, 500, -85)
        self.tempoSlider.Bind(wx.EVT_COMMAND_SCROLL, self.onSlider)
        self.tempoSpin = self.creator.SpinCtrl(-85, 500, globalVars.play.channelTempo, self.onSpin)
        # ピッチ変更
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.pitchLabel = self.creator.staticText(_("キー"),0)
        self.pitchSlider = self.creator.slider(_("キー"),150, globalVars.play.channelPitch, 60, -60)
        self.pitchSlider.Bind(wx.EVT_COMMAND_SCROLL, self.onSlider)
        self.pitchSpin = self.creator.SpinCtrl(-60, 60, globalVars.play.channelPitch, self.onSpin)
        # 周波数変更
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",)
        self.freqLabel = self.creator.staticText(_("周波数"),0)
        self.freqSlider = self.creator.slider(_("周波数"),150, globalVars.play.channelFreq, 400, 5)
        self.freqSlider.Bind(wx.EVT_COMMAND_SCROLL, self.onSlider)
        self.freqSpin = self.creator.SpinCtrl(5, 400, globalVars.play.channelFreq, self.onSpin)
        self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"", wx.ALIGN_RIGHT)
        self.bConfirm = self.creator.button(_("決定"),self.onButtonClick)
        self.bReset = self.creator.button(_("リセット"), self.onButtonClick)

    def GetData(self):
        return (self.tempoSlider.GetValue(), self.pitchSlider.GetValue(), self.freqSlider.GetValue())

    def onSpin(self, evt):
        obj = evt.GetEventObject()
        if obj == self.tempoSpin:
            self.tempoSlider.SetValue(obj.GetValue())
            globalVars.play.setTempo(obj.GetValue())
        elif obj == self.pitchSpin:
            self.pitchSlider.SetValue(obj.GetValue())
            globalVars.play.setPitch(obj.GetValue())
        elif obj == self.freqSpin:
            self.freqSlider.SetValue(obj.GetValue())
            globalVars.play.setFreq(obj.GetValue())


    def onSlider(self, evt):
        obj = evt.GetEventObject()
        if obj == self.tempoSlider:
            self.tempoSpin.SetValue(obj.GetValue())
            globalVars.play.setTempo(obj.GetValue())
        elif obj == self.pitchSlider:
            self.pitchSpin.SetValue(obj.GetValue())
            globalVars.play.setPitch(obj.GetValue())
        elif obj == self.freqSlider:
            self.freqSpin.SetValue(obj.GetValue())
            globalVars.play.setFreq(obj.GetValue())

    def onButtonClick(self, evt):
        if evt.GetEventObject()==self.bConfirm:
            self.wnd.EndModal(1)
        elif evt.GetEventObject()==self.bReset:
            self.tempoSlider.SetValue(0)
            self.tempoSpin.SetValue(0)
            globalVars.play.setTempo(0)
            self.pitchSlider.SetValue(0)
            self.pitchSpin.SetValue(0)
            globalVars.play.setPitch(0)
            self.freqSlider.SetValue(100)
            self.freqSpin.SetValue(100)
            globalVars.play.setFreq(100)
