import sys, platform, wx
import winsound
import globalVars
import lc_manager

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
        self.stopFlag = 0


    def freeBass(self):
        # bass.dllをフリー
        pybass.BASS_Free()

    def refreshView(self):
        # ボタン表示更新
        if self.stopFlag ==1 or globalVars.play.handle == 0:
            globalVars.app.hMainView.playPauseBtn.SetLabel("再生")
        elif globalVars.play.getChannelState() == pybass.BASS_ACTIVE_PLAYING:
            globalVars.app.hMainView.playPauseBtn.SetLabel("一時停止")
        else:
            globalVars.app.hMainView.playButton.SetLabel("再生")

        # リスト幅更新
        globalVars.app.hMainView.playlistView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        globalVars.app.hMainView.queueView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)


    def fileChange(self):
        # ストリームがないか停止状態であれば次のファイルを再生
        if globalVars.play.handle == 0 or globalVars.play.getChannelState() == pybass.BASS_ACTIVE_STOPPED:
            self.nextFile()

    def previousFile(self):
        p = False
        if self.stopFlag == 1:
            return None
        # プレイリスト再生中であれば
        get = globalVars.playlist.getFile()
        if get == globalVars.play.fileName:
            # プレイリストの1曲前を再生
            get = globalVars.playlist.getPrevious()
            if get != None:
                p = globalVars.play.inputFile(get)
        elif get != None:
            # キューなどからの復帰
            p = globalVars.play.inputFile(get)
        # 停止中フラグの解除
        if p: self.stopFlag = 0

    def playButtonControl(self):
        # 再生中は一時停止を実行
        if globalVars.play.getChannelState() == pybass.BASS_ACTIVE_PLAYING:
            globalVars.play.pauseChannel()
        # 停止中であればファイルを再生
        elif self.stopFlag == 1:
            self.stopFlag = 0
            self.nextFile()
        else:
            globalVars.play.channelPlay()

    def nextFile(self):
        # ユーザ操作による停止ではないか
        if self.stopFlag == 1:
            return None
        # キューを確認
        get = globalVars.queue.getNext()
        if get == None:
            # キューが空の時はプレイリストを確認
            get = globalVars.playlist.getNext()
            if get != None:
                globalVars.play.inputFile(get)

        else:
            globalVars.play.inputFile(get)

    def stop(self):
        self.stopFlag = 1
        globalVars.play.channelFree()
        globalVars.playlist.positionReset()

    def browseButton(self, evt):
        evtObj = evt.GetEventObject()
        if evtObj == globalVars.app.hMainView.addPlayListButton:
            fileDialog = wx.FileDialog(None, "ファイルを選択", style=wx.FD_OPEN | wx.FD_MULTIPLE)
            fileDialog.ShowModal()
            globalVars.playlist.addFiles(fileDialog.GetPaths())
        elif evtObj == globalVars.app.hMainView.addDirPlayListButton:
            dirDialog = wx.DirDialog(None, "フォルダを選択")
            dirDialog.ShowModal()
            globalVars.playlist.addFiles([dirDialog.GetPath()])
        elif evtObj == globalVars.app.hMainView.addQueueButton:
            fileDialog = wx.FileDialog(None, "ファイルを選択", style=wx.FD_OPEN | wx.FD_MULTIPLE)
            fileDialog.ShowModal()
            globalVars.queue.addFiles(fileDialog.GetPaths())

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
            globalVars.play.inputFile(lst.getFile(index, True))
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
