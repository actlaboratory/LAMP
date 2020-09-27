import globalVars
import event_processor
from soundPlayer.constants import *
from views import mkDialog

def previousFile():
    _previousFile(None, False)

def _previousFile(plIndex=None, slideOnce=False):
    if plIndex == None: plIndex = globalVars.playlist.playIndex #作業開始時のプレイリストポジション
    # プレイリスト再生中であれば
    get = globalVars.playlist.getFile()
    if get[1] == globalVars.eventProcess.playingDataNo:
        # プレイリストの1曲前を再生
        get = globalVars.playlist.getPrevious()
        if get[0] != None:
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex -= 1
                _previousFile(plIndex, True)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ループ指定の時は末尾へ
            get = globalVars.playlist.getFile(-1)
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex -= 1
                _previousFile(plIndex, True)
    elif get[0] != None:
        # キューなどからの復帰
        if slideOnce:
            globalVars.playlist.playIndex -= 1
            _previousFile(plIndex, False)
        elif not globalVars.eventProcess.play(globalVars.playlist, get):
            globalVars.playlist.playIndex -= 1
            _previousFile(plIndex, False)

    elif get == (None, None): _restoreIndex(plIndex)

def nextFile(plIndex=None):
    if plIndex == None: plIndex = globalVars.playlist.playIndex #作業開始時のプレイリストポジション
    # キューを確認
    get = globalVars.queue.getNext()
    if get[0] == None:
        # キューが空の時はプレイリストを確認
        get = globalVars.playlist.getNext()
        if get[0] != None:
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex += 1
                nextFile(plIndex)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ﾙｰﾌﾟであれば先頭へ
            get = globalVars.playlist.getFile(0)
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex += 1
                nextFile(plIndex)
        else: #再生終了後に次がなければ停止し、全消費スリープタイマーに通知
            _restoreIndex(plIndex)
            if globalVars.play.getStatus() == PLAYER_STATUS_END:
                globalVars.eventProcess.stop()
                globalVars.sleepTimer.call(True)
    else: #キューを再生
        _restoreIndex(plIndex)
        if not globalVars.eventProcess.play(globalVars.queue, get):
            globalVars.queue.playiIndex += 1
            nextFile(plIndex)

def _restoreIndex(plIndex):
    no = globalVars.eventProcess.playingDataNo
    try: path = globalVars.dataDict.dict[no][0]
    except KeyError as e: path = None
    index = globalVars.playlist.getIndex((path, no))
    if index == None: globalVars.playlist.setPlayIndex(plIndex) # 元の方
    else: globalVars.playlist.setPlayIndex(index) #新しいほう
