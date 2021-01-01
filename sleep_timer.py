# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx
import globalVars
import ctypes
import os
import time
from views import sleepTimerDialog, mkDialog

class sleepTimer():
    def __init__(self):
        self.sleepTimer = False #スリープタイマーオフ
        self.timeStarted = None
        self.fileCount = 0 #再生したファイル数
        self.fileTimer = False #ファイルタイマー
        self.allFileTimer = False #ファイル消費タイマー
        self.queueTimer = False #キュー消費タイマー
        self.endValue = None
        self.timer = None

    def set(self):
        if not self.check(): return
        self.sleepDialog = sleepTimerDialog.Dialog("sleepTimerDialog")
        self.sleepDialog.Initialize()
        r = self.sleepDialog.Show()
        if r == wx.ID_CANCEL:
            return
        self.setTimer(self.sleepDialog.GetData())

    def check(self):
        if not self.sleepTimer: return True
        m = _("スリープタイマーは起動中です。\n")
        if self.timeStarted != None:
            t = self._timeStr(self.timeStarted, self.timer.GetInterval() / 1000)
            if t != None: m = m + _("あと%sで発動し、以下を実行します。\n") % t
        elif self.fileTimer != False:
            m = m + _("あと、%d曲で、以下を実行します。\n") %(int(self.fileTimer) - self.fileCount)
        elif self.allFileTimer:
            m = m + _("すべての再生が完了したとき、以下を実行します。\n")
        elif self.queueTimer:
            m = m + _("キューの再生が完了したとき、以下を実行します。\n")
        m += _("動作: %s") % self.endValue
        d = mkDialog.Dialog("sleepIndicatorDialog")
        d.Initialize(_("作動状況"), m, (_("変更"), _("停止"), _("閉じる")))
        r = d.Show()
        if r == 1:
            self.__init__()
            if self.timer != None: self.timer.Stop()
        elif r == 0: return True
        return False


    def _timeStr(self, start, total):
        i = int(total) - int(time.time() - start)
        hour = 0
        min = 0
        sec = 0
        if i > 0: hour = i // 3600
        if i-(hour*3600) > 0: min = (i - hour) // 60
        if i-(hour*3600)-(min*60) > 0: sec = i - (hour*3600) - (min*60)
        l = []
        if hour > 0: l.append(_("%d時間") % hour)
        if min > 0: l.append(_("%d分") % min)
        l.append(_("%d秒") % sec)
        return "".join(l)
    
    #エラー処理後に呼び出す
    def setTimer(self, t):
        self.__init__()
        if self.timer != None: self.timer.Stop()
        if t[0] == self.sleepDialog.TIME_COUNTER:
            self.sleepTimer = True
            # タイマーの呼び出し
            self.timer = wx.Timer(globalVars.app.hMainView.hFrame)
            self.timer.Start((t[2]*(60**2)+t[3]*60)*1000) #ミリ秒タイマー
            self.timeStarted = time.time()
            globalVars.app.hMainView.hFrame.Bind(wx.EVT_TIMER, self.end, self.timer)
        elif t[0] == self.sleepDialog.PLAY_COUNTER:
            self.fileTimer = t[2]
        elif t[0] == self.sleepDialog.PLAY_END:
            self.allFileTimer = True
        elif t[0] == self.sleepDialog.QUEUE_END:
            self.queueTimer = True
        else:
            return
        self.sleepTimer = True
        self.endValue = t[1]

    def count(self):
        if self.sleepTimer == False:
            return
        if self.fileTimer != False: #ファイル数をカウント
            self.fileCount += 1
        self.call()

    def call(self, finished=False): #再生が終了したときに呼び出す（全ファイル消費=いいえ）
        if self.sleepTimer == False:
            return
        if self.fileTimer != False:
            if self.fileTimer == self.fileCount:
                self.end()
        elif self.allFileTimer == True:
            if finished == True:
                self.end()
        elif self.queueTimer == True:
            if len(globalVars.queue.lst) == 0:
                self.end()



    def end(self, evt=None):
        if self.endValue == _("再生の停止"):
            globalVars.eventProcess.stop()
            self.destroy()
        elif self.endValue == _("LAMPの終了"):
            globalVars.app.hMainView.hFrame.Destroy()
        elif self.endValue == _("コンピュータをスリープ"):
            globalVars.eventProcess.pause()
            self.destroy()
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        elif self.endValue == _("コンピュータの電源を切る"):
            os.system("shutdown -s")

    def destroy(self): #タイマー破棄
        self.__init__()
