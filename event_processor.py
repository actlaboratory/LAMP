import os, sys, platform, wx
import winsound
import globalVars
import lc_manager
import menuItemsStore
import view_manager
import settings
import data_dict
import file_manager
import shuffle_ctrl
import lampClipBoardCtrl
from soundPlayer.constants import *
from soundPlayer import fxPlayer
from views import mkDialog

class eventProcessor():
    def __init__(self):
        self.repeatLoopFlag = 0 #リピート=1, ループ=2
        self.tagInfoProcess = 0 # タグ情報表示フラグ 0=アルバム, 1=アーティスト, 2=アルバムアーティスト
        self.playingDataNo = None
        self.canFileChange = False # ファイル送りは１ファイル１回のみー
        self.muteFlag = 0 #初期値はミュート解除
        self.shuffleCtrl = 0

    def freeBass(self):
        # bass.dllをフリー
        globalVars.play.bassFree()

    def refreshView(self):
        #トラックバー更新
        max = globalVars.play.getLength()
        val = globalVars.play.getPosition()
        if max < 0:
            globalVars.app.hMainView.trackBar.SetMax(0)
            globalVars.app.hMainView.trackBar.Disable()
            self.setNowTimeLabel(0, 0)
        else:
            globalVars.app.hMainView.trackBar.SetMax(max)
            globalVars.app.hMainView.trackBar.Enable()
            if val == -1:
                globalVars.app.hMainView.trackBar.SetValue(0)
                globalVars.app.hMainView.trackBar.Disable()
                self.setNowTimeLabel(0, max)
            else:
                globalVars.app.hMainView.trackBar.SetValue(val)
                self.setNowTimeLabel(val, max)

        #ファイル送り
        if globalVars.play.getStatus() == PLAYER_STATUS_END:
                if self.canFileChange:
                    self.canFileChange = False
                    self.fileChange()

    # 曲情報更新
    def refreshTagInfo(self, evt=None):
        if evt == None: self.tagInfoProcess = 0
        if self.playingDataNo == None:
            globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : ")
            globalVars.app.hMainView.viewTagInfo.SetLabel("")
            globalV
        else:
            if globalVars.dataDict.dict[self.playingDataNo][3] == "": title = globalVars.dataDict.dict[self.playingDataNo][1] # ファイル名
            else: title = globalVars.dataDict.dict[self.playingDataNo][3] # タイトル
            if self.tagInfoProcess == 0: # アルバム名表示
                if globalVars.dataDict.dict[self.playingDataNo][6] == "": album = _("情報なし")
                else: album = globalVars.dataDict.dict[self.playingDataNo][6]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アルバム") + " : " + album)
                self.tagInfoProcess = 1
            elif self.tagInfoProcess == 1: # アーティスト情報表示
                if globalVars.dataDict.dict[self.playingDataNo][5] == "": artist = _("情報なし")
                else: artist = globalVars.dataDict.dict[self.playingDataNo][5]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アーティスト") + " : " + artist)
                self.tagInfoProcess = 2
            elif self.tagInfoProcess == 2: # アルバムアーティスト表示
                if globalVars.dataDict.dict[self.playingDataNo][7] == "": albumArtist = _("情報なし")
                else: albumArtist = globalVars.dataDict.dict[self.playingDataNo][6]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アルバムアーティスト") + " : " + albumArtist)
                self.tagInfoProcess = 0

        
        #ファイル戻し（巻き戻し用）
        if globalVars.play.getStatus() == PLAYER_STATUS_OVERREWIND:
            globalVars.play.overRewindOk()
            dataNoTmp = self.playingDataNo
            self.previousFile()
            if dataNoTmp != self.playingDataNo: globalVars.play.setPosition(globalVars.play.getLength() - 1)
            else: globalVars.play.stopOverRewind()

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
            globalVars.play.setVolume(0)
            self.muteFlag = 1
            globalVars.app.hMainView.volumeSlider.Disable()
            globalVars.app.hMainView.muteBtn.SetLabel("ﾐｭｰﾄ解除")
            globalVars.app.hMainView.menu.hVolumeInOperationMenu.SetLabel(menuItemsStore.getRef("MUTE"), _("消音を解除"))
        elif self.muteFlag == 1: #ミュート解除処理
            val = globalVars.app.hMainView.volumeSlider.GetValue()
            globalVars.play.setVolume(val)
            self.muteFlag = 0
            globalVars.app.hMainView.volumeSlider.Enable()
            globalVars.app.hMainView.muteBtn.SetLabel("ﾐｭｰﾄ")
            globalVars.app.hMainView.menu.hVolumeInOperationMenu.SetLabel(menuItemsStore.getRef("MUTE"), _("消音に設定"))

    #音量変更（変更幅+-%=変更しない, %指定=無視）
    def changeVolume(self, change=0, vol=-2): #vol=-1でデフォルト
        if self.muteFlag == 1: return None
        if change >= -100 and change <= 100 and change != 0:
            rtn = globalVars.play.setVolumeByDiff(change)
        elif change == 0 and vol == -1:
            globalVars.play.setVolume(100)
        elif change == 0 and vol <= 100 and vol >= 0:
            globalVars.play.setVolume(vol)
        rtn = globalVars.play.getConfig(PLAYER_CONFIG_VOLUME)
        globalVars.app.hMainView.volumeSlider.SetValue(rtn)
        globalVars.app.config["volume"]["default"] = str(int(rtn))


    def play(self, list=globalVars.playlist, listTpl=(None, None)):
        if globalVars.play.getStatus() == PLAYER_STATUS_DEVICEERROR:
            return False
        if listTpl == (None, None):
            rtn = False
        else:
            if globalVars.play.setSource(listTpl[0]):
                rtn = globalVars.play.play()
            else: rtn = False
        if list == globalVars.playlist:
            self.finalList = globalVars.playlist
            if rtn:
                globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))
                globalVars.sleepTimer.count() #スリープタイマーのファイル数カウント
                self.playingDataNo = listTpl[1]
                globalVars.dataDict.getTags([self.playingDataNo])
                globalVars.playlist.playIndex = globalVars.playlist.getIndex(listTpl)
                globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
                self.refreshTagInfo()
                globalVars.app.hMainView.tagInfoTimer.Start(10000)
                self.canFileChange = True # ファイル送りを許可
        elif list == globalVars.queue:
            self.finalList = globalVars.queue
            if rtn:
                globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))
                globalVars.sleepTimer.count() #スリープタイマーのファイル数カウント
                self.playingDataNo = listTpl[1]
                globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
                self.refreshTagInfo()
                globalVars.app.hMainView.tagInfoTimer.Start(10000)
                self.canFileChange = True # ファイル送りを許可
            globalVars.queue.deleteFile(globalVars.queue.getIndex(listTpl))
        if rtn == False:
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
            self.playError()
        return rtn

    def forcePlay(self, source):
        if globalVars.play.setSource(source):
            if globalVars.play.play():
                rtn = True
                self.playingDataNo = -1 #再生中のデータ番号を割り込み用に更新
                globalVars.dataDict.dict[-1] = (source, os.path.basename(sorted))
                globalVars.dataDict.getTags([-1])
                globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
            else: rtn = False
        else: rtn = False
        if rtn:
            globalVars.app.hMainView.playPauseBtn.SetLabel("一時停止")
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
            self.refreshTagInfo()
            globalVars.app.hMainView.tagInfoTimer.Start(10000)
        else:
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
            self.playError()
            self.canFileChange = True # ファイル送りを許可
        return rtn

    def playError(self):
        # 再生エラーの処理
        fxPlayer.playFx("./fx/error.mp3")
        d = mkDialog.Dialog("playErrorDialog")
        d.Initialize(_("再生時エラー"), _("このファイルは再生できません。"), (_("了解"),))
        d.Show()

    def pause(self, pause=True):
        if pause == True: #一時停止
            if globalVars.play.pause(): globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        else: #一時停止解除
            if globalVars.play.play(): globalVars.app.hMainView.playPauseBtn.SetLabel(_("一時停止"))

    #削除（リストオブジェクト, インデックス）
    def delete(self, lsObj, idx):
        rtn = lsObj.deleteFile(idx)
        if rtn != (None, None) and rtn == (globalVars.play.getConfig(PLAYER_CONFIG_SOURCE), self.playingDataNo):
            self.nextFile()
            self.pause()
        view_manager.changeListLabel(lsObj.getListCtrl())

    def fileChange(self, evt=None):
        globalVars.sleepTimer.call() #スリープタイマー問い合わせ
        #自動で次のファイルを再生
        self.nextFile()

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
        pos = globalVars.play.getPosition()
        if forward == True:
            globalVars.play.setPosition(pos+sec)
        else:
            globalVars.play.setPosition(pos-sec)
    
    def previousBtn(self):
        if globalVars.play.getPosition() <= 5:
            self.previousFile()
        else:
            globalVars.play.setPosition(0)

    def previousFile(self):
        if self.shuffleCtrl == 0:
            file_manager.previousFile()
        else:
            self.shuffleCtrl.previous()

    def playButtonControl(self):
        # 再生・一時停止を実行
        if globalVars.play.getStatus() == PLAYER_STATUS_PLAYING:
            self.pause()
        elif globalVars.play.getStatus() == PLAYER_STATUS_PAUSED:
            self.pause(False)
        # 停止中であればファイルを再生
        elif globalVars.play.getStatus() == PLAYER_STATUS_STOPPED:
            self.nextFile()
        else:
            self.play()

    def nextFile(self):
        if self.shuffleCtrl == 0:
            file_manager.nextFile()
        else:
            self.shuffleCtrl.next()

    def stop(self):
        globalVars.play.stop()
        globalVars.playlist.positionReset()
        globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
        self.playingDataNo = None
        globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") + " : ")
        globalVars.app.hMainView.viewTagInfo.SetLabel("")
        globalVars.app.hMainView.tagInfoTimer.Stop()

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
            globalVars.play.setRepeat(False)
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("ﾘﾋﾟｰﾄ / ﾙｰﾌﾟ")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("REPEAT_LOOP_NONE"), True)
        elif self.repeatLoopFlag == 1:
            globalVars.play.setRepeat(True)
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("只今: リピート")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_REPEAT"), True)
        elif self.repeatLoopFlag == 2:
            globalVars.play.setRepeat(False)
            globalVars.app.hMainView.repeatLoopBtn.SetLabel("只今: ループ")
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_LOOP"), True)

    def trackBarCtrl(self, bar):
        val = bar.GetValue()
        globalVars.play.setPosition(val)
    
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
