import wx
import globalVars
import ctypes
import os
from views import sleepTimerDialog

class sleepTimer():
    def __init__(self):
        self.sleepTimer = False #スリープタイマーオフ
        self.fileCount = 0 #再生したファイル数
        self.fileTimer = False #ファイルタイマー
        self.allFileTimer = False #ファイル消費タイマー
        self.queueTimer = False #キュー消費タイマー
        self.endValue = None

    def set(self):
        d = sleepTimerDialog.Dialog("sleepTimerDialog")
        d.Initialize()
        r = d.Show()
        if r == wx.ID_CANCEL:
            return
        self.setTimer(d.GetData())

    #エラー処理後に呼び出す
    def setTimer(self, t):
        if t[0] == _("次の時間が経過した"):
            self.sleepTimer = True
            # タイマーの呼び出し
            self.timer = wx.Timer(globalVars.app.hMainView.hFrame)
            self.timer.Start((t[2]*(60**2)+t[3]*60)*1000) #ミリ秒タイマー
            globalVars.app.hMainView.hFrame.Bind(wx.EVT_TIMER, self.end, self.timer)
        elif t[0] == _("次の曲数を再生した"):
            self.fileTimer = t[2]
        elif t[0] == _("すべての再生が完了した"):
            self.allFileTimer = True
        elif t[0] == _("キューの再生を完了した"):
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
