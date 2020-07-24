import os, sys, platform, wx
import winsound
import globalVars
import lc_manager
import menuItemsStore
import player
import settings
import file_manager
import shuffle_ctrl
import lampClipBoardCtrl

def is64Bit():
    return sys.maxsize > 2 ** 32

#使用環境に応じて適切なdllをロード
if is64Bit():
    from pybass64 import pybass
    from pybass64 import bass_fx
else:
    from pybass import pybass
    from pybass import bass_fx

class eventProcessor():
    def __init__(self):
        self.timeoutTimer = None #読み込みタイムアウトタイマー
        self.repeatLoopFlag = 0 #リピート=1, ループ=2
        self.playingDataNo = None
        self.muteFlag = 0 #初期値はミュート解除
        self.shuffleCtrl = 0

    def freeBass(self):
        # bass.dllをフリー
        pybass.BASS_Free()

    def refreshView(self):
        #デバイス変更
        if pybass.BASS_ErrorGetCode() == pybass.BASS_ERROR_START or globalVars.play.getChannelState() == player.state.PAUSED_DEVICE:
            if globalVars.play.restartDevice(): globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))

        #トラックバー更新
        max = globalVars.play.getChannelLength()
        val = globalVars.play.getChannelPosition()
        if max != False and (globalVars.play.getChannelState() == player.state.PLAYING or globalVars.play.getChannelState() == player.state.PAUSED):
            if max < 0:
                globalVars.app.hMainView.trackBar.SetMax(0)
                globalVars.app.hMainView.trackBar.Disable()
            else:
                globalVars.app.hMainView.trackBar.SetMax(max)
                globalVars.app.hMainView.trackBar.Enable()
            if val == False:
                globalVars.app.hMainView.trackBar.SetValue(0)
                self.setNowTimeLabel(0, 0)
            else:
                globalVars.app.hMainView.trackBar.SetValue(val)
                self.setNowTimeLabel(val, max)
        else:
            globalVars.app.hMainView.trackBar.Disable()
            globalVars.app.hMainView.trackBar.SetMax(0)
            globalVars.app.hMainView.trackBar.SetValue(0)
            self.setNowTimeLabel(0, 0)
            if globalVars.play.getChannelState() == player.state.STOPED:
                if not(val != 0 and val == max): #読み込みタイムアウトまでは進めない
                    if self.timeoutTimer == None:
                        self.timeoutTimer = wx.Timer(globalVars.app.hMainView.hFrame)
                    if self.timeoutTimer.IsRunning() == False: #タイムアウト処理
                        if os.path.isfile(globalVars.play.fileName):
                            t = 1000
                        else:
                            t = 10000
                        self.timeoutTimer.Start(t)
                        globalVars.app.hMainView.hFrame.Bind(wx.EVT_TIMER, self.fileChange, self.timeoutTimer)
                else:
                    self.fileChange()

    #経過時間表示を更新
    def setNowTimeLabel(self, now, max):
        time = []
        for f in (now, max):
            i = int(f)
            hour = 0
            min = 0
            sec = 0
            if i > 0: hour = i // 3600
            if i-(hour*3600) > 0: min = (i - hour) // 60
            if i-(hour*3600)-(min*60) > 0: sec = i - (hour*3600) - (min*60)
            time.append(f"{hour:01}:{min:02}:{sec:02}")
        if globalVars.app.hMainView.nowTime.GetLabel() != time[0]+" / "+time[1]:
            globalVars.app.hMainView.nowTime.SetLabel(time[0] + " / " + time[1])

    def mute(self):
        if self.muteFlag == 0: #ミュート処理
            globalVars.play.changeVolume(0)
            self.muteFlag = 1
            globalVars.app.hMainView.volumeSlider.Disable()
            globalVars.app.hMainView.muteBtn.SetLabel("ﾐｭｰﾄ解除")
            globalVars.app.hMainView.menu.hVolumeInOperationMenu.SetLabel(menuItemsStore.getRef("MUTE"), _("消音を解除"))
        elif self.muteFlag == 1: #ミュート解除処理
            val = globalVars.app.hMainView.volumeSlider.GetValue()
            globalVars.play.changeVolume(val)
            self.muteFlag = 0
            globalVars.app.hMainView.volumeSlider.Enable()
            globalVars.app.hMainView.muteBtn.SetLabel("ﾐｭｰﾄ")
            globalVars.app.hMainView.menu.hVolumeInOperationMenu.SetLabel(menuItemsStore.getRef("MUTE"), _("消音に設定"))

    #音量変更（変更幅+-%=変更しない, %指定=無視）
    def changeVolume(self, change=0, vol=-2): #vol=-1でデフォルト
        if self.muteFlag == 1: return None
        if change >= -100 and change <= 100 and change != 0:
            vol = globalVars.play.getVolume() + change
            rtn = globalVars.play.changeVolume(vol)
        elif change == 0 and vol == -1:
            globalVars.play.changeVolume(100)
        elif change == 0 and vol <= 200 and vol >= 0:
            globalVars.play.changeVolume(vol)
        rtn= globalVars.play.getVolume()
        globalVars.app.hMainView.volumeSlider.SetValue(rtn)
        globalVars.app.config["volume"]["default"] = str(int(rtn))


    def play(self, list=globalVars.playlist, listTpl=(None, None)):
        if listTpl == (None, None):
            rtn = False
        else:
            rtn = globalVars.play.inputFile(listTpl[0])
        self.playingDataNo = listTpl[1]
        if list == globalVars.playlist:
            self.finalList = globalVars.playlist
            if rtn:
                globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))
                globalVars.sleepTimer.count() #スリープタイマーのファイル数カウント
            globalVars.playlist.playIndex = globalVars.playlist.getIndex(listTpl)
        elif list == globalVars.queue:
            self.finalList = globalVars.queue
            if rtn:
                globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))
                globalVars.sleepTimer.count() #スリープタイマーのファイル数カウント
            globalVars.queue.deleteFile(globalVars.queue.getIndex(listTpl))
        if rtn == False:
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")

    def pause(self, pause=True):
        if pause == True: #一時停止
            if globalVars.play.pauseChannel():
                globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        else: #一時停止解除
            if globalVars.play.channelPlay():

                globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))

    #削除（リストオブジェクト, インデックス）
    def delete(self, lsObj, idx):
        rtn = lsObj.deleteFile(idx)
        if rtn != (None, None) and rtn == (globalVars.play.fileName, self.playingDataNo):
            self.nextFile()
            self.pause()

    def fileChange(self, evt=None):
        # 再生が継続できた場合
        if evt != None:
            if globalVars.play.getChannelState() == player.state.PLAYING:
                self.timeoutTimer.Stop()
                return None
        if globalVars.play.rewindFlag == 1: # 巻き戻し中に先頭になった場合
            self.timeoutTimer.Stop()
            self.play(self.finalList, (globalVars.play.fileName, self.playingDataNo))
            return None
        globalVars.sleepTimer.call() #スリープタイマー問い合わせ
        #自動で次のファイルを再生
        if self.repeatLoopFlag == 1: #リピート
            self.play(self.finalList, (globalVars.play.fileName, self.playingDataNo))
        else: #それ以外（nextFileがループ処理）
            self.nextFile()
        if self.timeoutTimer != None: #タイムアウト終了
            self.timeoutTimer.Stop()

    #スキップ間隔設定(増加=はい, 秒数直接指定=なし)
    def setSkipInterval(self, increase=True, sec=None):
        if sec == None:
            sec = settings.getSkipInterval()[0]
        idx = settings.skipInterval.index(sec)
        if increase == True:
            if idx < len(settings.skipInterval)-1:
                settings.setSkipInterval(settings.skipInterval[idx+1])
        else:
            if idx > 0:
                settings.setSkipInterval(settings.skipInterval[idx-1])
        strVal = settings.getSkipInterval()[1]
        globalVars.app.hMainView.menu.hOperationMenu.SetLabel(menuItemsStore.getRef("SKIP"), strVal+" "+_("進む"))
        globalVars.app.hMainView.menu.hOperationMenu.SetLabel(menuItemsStore.getRef("REVERSE_SKIP"), strVal+" "+_("戻る"))

    #スキップ（秒, 方向=進む)
    def skip(self, sec, forward=True):
        pos = globalVars.play.getChannelPosition()
        if forward == True:
            globalVars.play.setChannelPosition(pos+sec)
        else:
            globalVars.play.setChannelPosition(pos-sec)
    
    def previousBtn(self):
        if globalVars.play.getChannelPosition() <= 5:
            self.previousFile()
        else:
            globalVars.play.setChannelPosition(0)

    def previousFile(self):
        if self.shuffleCtrl == 0:
            file_manager.previousFile()
        else:
            self.shuffleCtrl.previous()

    def playButtonControl(self):
        # 再生・一時停止を実行
        if globalVars.play.getChannelState() == player.state.PLAYING:
            self.pause()
        elif globalVars.play.getChannelState() == player.state.PAUSED:
            self.pause(False)
        # 停止中であればファイルを再生
        elif globalVars.play.getChannelState() == player.state.COLD:
            self.nextFile()
        else:
            self.play()

    def nextFile(self):
        if self.shuffleCtrl == 0:
            file_manager.nextFile()
        else:
            self.shuffleCtrl.next()

    def stop(self):
        if self.timeoutTimer != None:
            self.timeoutTimer.Stop()
        globalVars.play.channelFree()
        globalVars.playlist.positionReset()
        globalVars.play.handle = 0
        globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        self.playingDataNo = None

    def shuffleSw(self):
        if self.shuffleCtrl == 0:
            self.shuffleCtrl = shuffle_ctrl.shuffle(globalVars.playlist)
            globalVars.app.hMainView.shuffleBtn.SetLabel(_("ｼｬｯﾌﾙ解除"))
            globalVars.app.hMainView.menu.hOperationMenu.Check(menuItemsStore.getRef("SHUFFLE"), True)
        else: #シャッフルを解除してプレイリストに復帰
            idx = globalVars.playlist.getIndex(self.shuffleCtrl.getNow())
            if idx != None:
                globalVars.playlist.playIndex = idx
            else:
                globalVars.playlist.positionReset()
            self.shuffleCtrl = 0
            globalVars.app.hMainView.shuffleBtn.SetLabel(_("ｼｬｯﾌﾙ"))
            globalVars.app.hMainView.menu.hOperationMenu.Check(menuItemsStore.getRef("SHUFFLE"), False)

    #リピートﾙｰﾌﾟフラグを切り替え(モード=順次)
    def repeatLoopCtrl(self, mode=-1): #0=なし, 1=リピート, 2=ループ
        if mode == -1:
            if self.repeatLoopFlag < 2:
                self.repeatLoopFlag+=1
            else:
                self.repeatLoopFlag=0
        elif mode>=0 and mode<=2:
            self.repeatLoopFlag = mode
        if self.repeatLoopFlag == 0:
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("ﾘﾋﾟｰﾄ / ﾙｰﾌﾟ")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("REPEAT_LOOP_NONE"), True)
        elif self.repeatLoopFlag == 1:
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("只今: リピート")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_REPEAT"), True)
        elif self.repeatLoopFlag == 2:
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("只今: ループ")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_LOOP"), True)

    def trackBarCtrl(self, bar):
        val = bar.GetValue()
        globalVars.play.setChannelPosition(val)
    
    #リストビューアクティブのイベント処理
    def listActivate(self, evt):
        self.listSelection(evt.GetEventObject())
    
    # リストビューで選択されたアイテムの処理
    def listSelection(self, evtObj):
        if evtObj == globalVars.app.hMainView.playlistView:
            lst = globalVars.playlist
        elif evtObj == globalVars.app.hMainView.queueView:
            lst = globalVars.queue
        # 単一選択時アクティベートされた曲を再生
        iLst = lc_manager.getListCtrlSelections(evtObj)
        if len(iLst) == 1:
            index = iLst[0]
            p = globalVars.eventProcess.play(lst, lst.getFile(index))
