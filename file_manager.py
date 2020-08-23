import globalVars
import event_processor
from bassPlayer.constants import *

def previousFile():
    # プレイリスト再生中であれば
    get = globalVars.playlist.getFile()
    if get[1] == globalVars.eventProcess.playingDataNo:
        # プレイリストの1曲前を再生
        get = globalVars.playlist.getPrevious()
        if get[0] != None:
            globalVars.eventProcess.play(globalVars.playlist, get)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ループ指定の時は末尾へ
            get = globalVars.playlist.getFile(-1)
            globalVars.eventProcess.play(globalVars.playlist, get)
    elif get[0] != None:
        # キューなどからの復帰
        globalVars.eventProcess.play(globalVars.playlist, get)

def nextFile():
    # キューを確認
    get = globalVars.queue.getNext()
    if get[0] == None:
        # キューが空の時はプレイリストを確認
        get = globalVars.playlist.getNext()
        if get[0] != None:
            globalVars.eventProcess.play(globalVars.playlist, get)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ﾙｰﾌﾟであれば先頭へ
            get = globalVars.playlist.getFile(0)
            globalVars.eventProcess.play(globalVars.playlist, get)
        else: #再生終了後に次がなければ停止し、全消費スリープタイマーに通知
            if globalVars.play.getStatus() == PLAYER_STATUS_EOF or globalVars.play.getStatus() == PLAYER_STATUS_STREAMEND:
                globalVars.eventProcess.stop()
                globalVars.sleepTimer.call(True)
    else: #キューを再生
        globalVars.eventProcess.play(globalVars.queue, get)
