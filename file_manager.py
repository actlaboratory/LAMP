import globalVars
import event_processor
from soundPlayer.constants import *
from views import mkDialog

def previousFile():
    # プレイリスト再生中であれば
    get = globalVars.playlist.getFile()
    if get[1] == globalVars.eventProcess.playingDataNo:
        # プレイリストの1曲前を再生
        get = globalVars.playlist.getPrevious()
        if get[0] != None:
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex -= 1
                previousFile()
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ループ指定の時は末尾へ
            get = globalVars.playlist.getFile(-1)
            if not globalVars.eventProcess.play(globalVars.playlist, get):
                globalVars.playlist.playIndex -= 1
                previousFile
    elif get[0] != None:
        # キューなどからの復帰
        if not globalVars.eventProcess.play(globalVars.playlist, get):
            globalVars.playlist.playIndex -= 1
            previousFile()

def nextFile(plIndex=None):
    no = globalVars.eventProcess.playingDataNo
    try: path = globalVars.dataDict.dict[no][0]
    except KeyError as e: path = None
    if plIndex == None: plIndex = globalVars.playlist.getIndex((path, no))
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
            globalVars.playlist.setPlayIndex(plIndex)
            if globalVars.play.getStatus() == PLAYER_STATUS_END:
                globalVars.eventProcess.stop()
                globalVars.sleepTimer.call(True)
    else: #キューを再生
        globalVars.playlist.setPlayiIndex(plIndex)
        if not globalVars.eventProcess.play(globalVars.queue, get):
            globalVars.queue.playiIndex += 1
            nextFile(plIndex)
