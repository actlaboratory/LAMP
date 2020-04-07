import sys, platform, wx
import winsound
import globalVars
import lc_manager
import menuItemsStore
import player

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
        self.repeatLoopFlag = 0 #リピート=1, ループ=2
        self.playingDataNo = None

    def freeBass(self):
        # bass.dllをフリー
        pybass.BASS_Free()

    def refreshView(self):
        #トラックバー更新
        max = globalVars.play.getChannelLength()
        val = globalVars.play.getChannelPosition()
        if max != False and (globalVars.play.getChannelState() == player.state.PLAYING or globalVars.play.getChannelState() == player.state.PAUSED):
            globalVars.app.hMainView.trackBar.SetMax(max)
            if val == False:
                globalVars.app.hMainView.trackBar.SetValue(0)
            else:
                globalVars.app.hMainView.trackBar.SetValue(val)
        else:
            globalVars.app.hMainView.trackBar.SetMax(0)
            globalVars.app.hMainView.trackBar.SetValue(0)
            if globalVars.play.getChannelState() == player.state.STOPED:
                self.fileChange()

        # リスト幅更新
        globalVars.app.hMainView.playlistView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        globalVars.app.hMainView.queueView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
    #音量変更（変更幅+-%=変更しない, %指定=無視）
    def changeVolume(self, change=0, vol=-2): #vol=-1でデフォルト
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


    def play(self, listTpl=None):
        if listTpl == None:
            rtn = globalVars.play.channelPlay()
        else:
            rtn = globalVars.play.inputFile(listTpl[0])
            if rtn:
                self.playingDataNo = listTpl[1]
        if rtn:
            globalVars.app.hMainView.playPauseBtn.SetLabel("一時停止")
        else:
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")

    def pause(self):
        if globalVars.play.pauseChannel():
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")

    def fileChange(self):
        #自動で次のファイルを再生
        if self.repeatLoopFlag == 1: #リピート
            self.play((globalVars.play.fileName, self.playingDataNo))
        else: #それ以外（nextFileがループ処理）
            self.nextFile()

    def previousBtn(self):
        if globalVars.play.getChannelPosition() <= 5:
            self.previousFile()
        else:
            globalVars.play.setChannelPosition(0)

    def previousFile(self):
        # プレイリスト再生中であれば
        get = globalVars.playlist.getFile()
        if get[1] == self.playingDataNo:
            # プレイリストの1曲前を再生
            get = globalVars.playlist.getPrevious()
            if get[0] != None:
                self.play(get)
            elif self.repeatLoopFlag == 2: #ループ指定の時は末尾へ
                get = globalVars.playlist.getFile(-1, True)
                if get[0] != None:
                    self.play(get)
        elif get[0] != None:
            # キューなどからの復帰
            self.play(get)

    def playButtonControl(self):
        # 再生中は一時停止を実行
        if globalVars.play.getChannelState() == player.state.PLAYING:
            self.pause()
        # 停止中であればファイルを再生
        elif globalVars.play.getChannelState() == player.state.COLD:
            self.nextFile()
        else:
            self.play()

    def nextFile(self):
        # キューを確認
        get = globalVars.queue.getNext()
        if get[0] == None:
            # キューが空の時はプレイリストを確認
            get = globalVars.playlist.getNext()
            if get[0] != None:
                self.play(get)
            elif self.repeatLoopFlag == 2: #ﾙｰﾌﾟであれば先頭へ
                get = globalVars.playlist.getFile(0,True)
                if get[0] != None:
                    self.play(get)
            else: #再生終了後に次がなければ停止とする
                if globalVars.play.getChannelState() == player.state.STOPED:
                    self.stop()
        else:
            self.play(get)

    def stop(self):
        globalVars.play.channelFree()
        globalVars.playlist.positionReset()
        globalVars.play.handle = False
        globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        self.playingDataNo = None

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
    
    # リストビューでアクティベートされたアイテムの処理
    def listSelection(self, evt):
        evtObj = evt.GetEventObject()
        if evtObj == globalVars.app.hMainView.playlistView:
            lst = globalVars.playlist
        elif evtObj == globalVars.app.hMainView.queueView:
            lst = globalVars.queue
        # 単一選択時アクティベートされた曲を再生
        iLst = lc_manager.getListCtrlSelections(evtObj)
        if len(iLst) == 1:
            index = evt.GetIndex()
            p = globalVars.eventProcess.play(lst.getFile(index, True))
            if lst == globalVars.queue:
                lst.deleteFile(index)

    def listViewKeyEvent(self, evt):
        evtObj = evt.GetEventObject()
        # 発生元とpythonリストの対応付け
        if evtObj == globalVars.app.hMainView.playlistView:
            lst = globalVars.playlist
        elif evtObj == globalVars.app.hMainView.queueView:
            lst = globalVars.queue
        kc = evt.GetKeyCode()
        # deleteで削除
        if kc == wx.WXK_DELETE:
            index = lc_manager.getListCtrlSelections(evtObj)
            cnt = 0
            for i in index:
                i = i-cnt
                lst.deleteFile(i)
                cnt += 1
