import os, sys, platform, wx
import winsound
import globalVars
import constants
import errorCodes
import menuItemsStore
import fxManager
import listManager
import view_manager
import settings
import shuffle_ctrl
import lampClipBoardCtrl
from soundPlayer.constants import *
from soundPlayer import fxPlayer
from views import mkDialog


class eventProcessor():
    def __init__(self):
        self.repeatLoopFlag = 0 #リピート=1, ループ=2
        self.playingList = None
        self.tagInfoProcess = 0 # タグ情報表示フラグ 0=アルバム, 1=アーティスト, 2=アルバムアーティスト
        self.muteFlag = False #初期値はミュート解除
        self.shuffleCtrl = None
        self.fileChanging = False # ファイル送りの多重呼び出し防止

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
            globalVars.sleepTimer.count() #スリープタイマーのファイル数カウント
            if globalVars.app.config.getboolean("player", "manualSongFeed", False):
                self.pause(True, True)
            else:
                if self.fileChange() == False:
                    self.stop()

        #ファイル戻し（巻き戻し用）
        if globalVars.play.getStatus() == PLAYER_STATUS_OVERREWIND:
            globalVars.play.overRewindOk() # プレイヤーに応答
            if self.previousFile() == True: # 前の曲があったら末尾へ
                globalVars.play.setPosition(globalVars.play.getLength() - 1)

    # 曲情報更新
    def refreshTagInfo(self, evt=None):
        if evt == None: self.tagInfoProcess = 0
        if self.playingList == None:
            globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : ")
            globalVars.app.hMainView.viewTagInfo.SetLabel("")
        else:
            if self.playingList == constants.PLAYLIST: t = listManager.getTuple(constants.PLAYLIST)
            else: t = globalVars.listInfo.playingTmp
            if t[constants.ITEM_TITLE] == "": title = t[constants.ITEM_NAME] # ファイル名
            else: title = t[constants.ITEM_TITLE] # タイトル
            if self.tagInfoProcess == 0: # アルバム名表示
                if t[constants.ITEM_ALBUM] == "": album = _("情報なし")
                else: album = t[constants.ITEM_ALBUM]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アルバム") + " : " + album)
                self.tagInfoProcess = 1
            elif self.tagInfoProcess == 1: # アーティスト情報表示
                if t[constants.ITEM_ARTIST] == "": artist = _("情報なし")
                else: artist = t[constants.ITEM_ARTIST]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アーティスト") + " : " + artist)
                self.tagInfoProcess = 2
            elif self.tagInfoProcess == 2: # アルバムアーティスト表示
                if t[constants.ITEM_ALBUMARTIST] == "": albumArtist = _("情報なし")
                else: albumArtist = t[constants.ITEM_ALBUMARTIST]
                globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") +  " : " + title)
                globalVars.app.hMainView.viewTagInfo.SetLabel(_("アルバムアーティスト") + " : " + albumArtist)
                self.tagInfoProcess = 0

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
        if not self.muteFlag: #ミュート処理
            globalVars.play.setVolume(0)
            self.muteFlag = True
            globalVars.app.hMainView.volumeSlider.Disable()
            view_manager.buttonSetMuteOn()
            globalVars.app.hMainView.menu.hVolumeInOperationMenu.SetLabel(menuItemsStore.getRef("MUTE"), _("消音を解除"))
        elif self.muteFlag: #ミュート解除処理
            val = globalVars.app.hMainView.volumeSlider.GetValue()
            globalVars.play.setVolume(val)
            self.muteFlag = False
            globalVars.app.hMainView.volumeSlider.Enable()
            view_manager.buttonSetMuteOff()
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


    # ファイルの新規再生
    def play(self, listPorQ=constants.PLAYLIST):
        if not globalVars.play.isDeviceOk(): return False #デバイス異常時は処理を中止
        if globalVars.play.getStatus() == PLAYER_STATUS_DEVICEERROR:
            return False
        t = listManager.getTuple(listPorQ, True)
        if listPorQ == constants.QUEUE: globalVars.listInfo.playingTmp = t #キュー再生の時はタプルを一時退避
        if globalVars.play.setSource(t[constants.ITEM_PATH]):
            ret = globalVars.play.play()
        else: ret = False
        if ret:
            self.playingList = listPorQ
            if ret:
                view_manager.buttonSetPause()
                listManager.setTag(listPorQ)
                globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
                self.refreshTagInfo()
                globalVars.app.hMainView.tagInfoTimer.Start(10000)
            view_manager.setFileStaticInfoView() #スクリーンリーダ用リストとウィンドウ情報更新
        if not ret:
            view_manager.buttonSetPlay()
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
            view_manager.clearStaticInfoView() #スクリーンリーダ用リストとウィンドウ情報更新
        return ret

    def forcePlay(self, source):
        if not globalVars.play.isDeviceOk(): return False #デバイス異常時は処理を中止
        if globalVars.play.setSource(source):
            if globalVars.play.play():
                ret = True
                self.playingList = constants.NOLIST # リストではない
                globalVars.listInfo.playingTmp = (source, os.path.basename(source), 0)
                listManager.setTag(constants.NOLIST)
                globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
            else: ret = False
        else: ret = False
        if ret:
            view_manager.buttonSetPause()
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), True)
            self.refreshTagInfo()
            globalVars.app.hMainView.tagInfoTimer.Start(10000)
            view_manager.setFileStaticInfoView() #スクリーンリーダ用リストとウィンドウ情報更新
        else:
            view_manager.buttonSetPlay()
            globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
            view_manager.clearStaticInfoView() #スクリーンリーダ用リストとウィンドウ情報更新
        return ret

    def playError(self):
        # 再生エラーの処理
        if globalVars.app.config.getboolean("notification", "ignoreError", True): return 0
        fxManager.error()
        d = mkDialog.Dialog("playErrorDialog")
        d.Initialize(_("再生時エラー"), _("このファイルは再生できません。"), (_("継続"),_("停止")))
        return d.Show()

    def pause(self, pause=True, force=False):
        if pause == True: #一時停止
            if globalVars.play.pause() or force: view_manager.buttonSetPlay()
        else: #一時停止解除
            if globalVars.play.play(): view_manager.buttonSetPause()

    #削除（リストオブジェクト, インデックス）
    def delete(self, lcObj):
        if lcObj.GetSelectedItemCount() == len(lcObj): # 全選択中ならクリア
            lcObj.clear()
            self.stop()
        else:
            # 選択済みアイテムリストを生成
            first = lcObj.GetFirstSelected()
            if first < 0: return
            else: 
                itm = [[first]]
                nextTmp = first
                if lcObj == listManager.getLCObject(self.playingList) and lcObj.getPointer() == first:
                    self.stop() # 再生中の曲を削除するときは停止
            while True:
                next = lcObj.GetNextSelected(nextTmp)
                if lcObj == listManager.getLCObject(self.playingList) and lcObj.getPointer() == next:
                    self.stop() # 再生中の曲を削除するときは停止
                if next < 0:
                    if itm[-1][0] != nextTmp: itm[-1].append(nextTmp)
                    break
                else:
                    if next - nextTmp != 1:
                        itm[-1].append(nextTmp)
                        itm.append([next])
                    nextTmp = next
            count = 0 # カウンタをリセットして削除開始
            for l in itm:
                if len(l) == 2:
                    del lcObj[l[0] - count: l[1] - count + 1]
                    count += l[1] - l[0] + 1
                else:
                    del lcObj[l[0] - count]
                    count += 1
        view_manager.changeListLabel(lcObj)

    def fileChange(self, evt=None):
        self.fileChanging = True
        globalVars.sleepTimer.call() #スリープタイマー問い合わせ
        #自動で次のファイルを再生
        ret = self.nextFile()
        self.fileChanging = False
        return ret

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
        globalVars.app.hMainView.notification.show(strVal + _("スキップ"), 2)
        globalVars.app.say(strVal)

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
        if not globalVars.play.isDeviceOk(): return False
        if self.shuffleCtrl == None:
            ret = listManager.previous(self.playingList)
        else:
            ret = self.shuffleCtrl.previous(self.playingList)
        if ret == False:
            if self.playError() == constants.DIALOG_PE_CONTINUE:
                self.playingList = constants.PLAYLIST
                self.previousFile()
            else: self.stop()
            return False
        elif ret == errorCodes.END:
            return False
        else: return True

    def playButtonControl(self):
        # 再生・一時停止を実行
        s = globalVars.play.getStatus()
        if s == PLAYER_STATUS_DEVICEERROR: return
        if s == PLAYER_STATUS_PLAYING:
            self.pause()
        elif globalVars.play.getStatus() == PLAYER_STATUS_PAUSED:
            self.pause(False)
        # 停止中であればファイルを再生
        elif globalVars.play.getStatus() == PLAYER_STATUS_STOPPED:
            self.nextFile()
        else:
            if globalVars.play.play(): view_manager.buttonSetPause()
            else: view_manager.buttonSetPlay()

    def nextFile(self):
        if not globalVars.play.isDeviceOk():
            return False
        if self.shuffleCtrl == None:
            ret = listManager.next(self.playingList)
        else:
            ret = self.shuffleCtrl.next()
        if ret == False:
            if self.playError() == constants.DIALOG_PE_CONTINUE:
                self.playingList = constants.PLAYLIST
                self.nextFile()
            else: self.stop()
            return False
        elif ret == errorCodes.END:
            return False
        else: return True

    def stop(self):
        view_manager.clearStaticInfoView() #スクリーンリーダ用リストの更新
        globalVars.app.hMainView.playlistView.setPointer(-1)
        globalVars.play.stop()
        view_manager.buttonSetPlay()
        globalVars.app.hMainView.menu.hFunctionMenu.Enable(menuItemsStore.getRef("ABOUT_PLAYING"), False)
        globalVars.app.hMainView.viewTitle.SetLabel(_("タイトル") + " : ")
        globalVars.app.hMainView.viewTagInfo.SetLabel("")
        globalVars.app.hMainView.tagInfoTimer.Stop()

    def shuffleSw(self):
        if self.shuffleCtrl == None:
            self.shuffleCtrl = shuffle_ctrl.shuffle(listManager.getLCObject(constants.PLAYLIST))
            view_manager.buttonSetShuffleOn()
            globalVars.app.say(_("シャッフル"))
            globalVars.app.hMainView.menu.hOperationMenu.Check(menuItemsStore.getRef("SHUFFLE"), True)
        else: #シャッフルを解除してプレイリストに復帰
            self.shuffleCtrl = None
            view_manager.buttonSetShuffleOff()
            globalVars.app.say(_("オフ"))
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
            view_manager.buttonSetRepeatLoop()
            globalVars.app.say(_("オフ"))
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("REPEAT_LOOP_NONE"), True)
        elif self.repeatLoopFlag == 1:
            globalVars.play.setRepeat(True)
            view_manager.buttonSetRepeat()
            globalVars.app.say(_("リピート"))
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_REPEAT"), True)
        elif self.repeatLoopFlag == 2:
            globalVars.play.setRepeat(False)
            view_manager.buttonSetLoop()
            globalVars.app.say(_("ループ"))
            globalVars.app.hMainView.menu.hRepeatLoopInOperationMenu.Check(menuItemsStore.getRef("RL_LOOP"), True)

    def trackBarCtrl(self, bar):
        val = bar.GetValue()
        globalVars.play.setPosition(val)
    
    #リストビューアクティブのイベント処理
    def listActivate(self, evt):
        self.listSelection(evt.GetEventObject())
    
    # リストビューで選択されたアイテムの処理
    def listSelection(self, evtObj):
        if not globalVars.play.isDeviceOk(): return False #デバイス異常時は処理を中止
        if evtObj == globalVars.app.hMainView.playlistView:
            lst = constants.PLAYLIST
        elif evtObj == globalVars.app.hMainView.queueView:
            lst = constants.QUEUE
        # 単一選択時アクティベートされた曲を再生
        if evtObj.GetSelectedItemCount() == 1:
            evtObj.setPointer(evtObj.GetFirstSelected())
            p = self.play(lst)

    def setSongFeed(self):
        if globalVars.app.config.getboolean("player", "manualSongFeed", False):
            globalVars.app.config["player"]["manualSongFeed"] = False
            globalVars.app.hMainView.notification.show(_("曲送りは自動"), 2)
            globalVars.app.say(_("曲送りは自動"))
        else:
            globalVars.app.config["player"]["manualSongFeed"] = True
            globalVars.app.hMainView.notification.show(_("曲送りは手動"), 2)
            globalVars.app.say(_("曲送りは手動"))
        