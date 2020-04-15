import globalVars
import player

def previousFile():
    # プレイリスト再生中であれば
    get = globalVars.playlist.getFile()
    if get[1] == globalVars.eventProcess.playingDataNo or get[1] == None:
        # プレイリストの1曲前を再生
        get = globalVars.playlist.getPrevious()
        if get[0] != None:
            globalVars.eventProcess.play(get)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ループ指定の時は末尾へ
            get = globalVars.playlist.getFile(-1, True)
            if get[0] != None:
                globalVars.eventProcess.play(get)
    elif get[0] != None:
        # キューなどからの復帰
        globalVars.eventProcess.play(get)

def nextFile():
    # キューを確認
    get = globalVars.queue.getNext()
    if get[0] == None:
        # キューが空の時はプレイリストを確認
        get = globalVars.playlist.getNext()
        if get[0] != None:
            globalVars.eventProcess.play(get)
        elif globalVars.eventProcess.repeatLoopFlag == 2: #ﾙｰﾌﾟであれば先頭へ
            get = globalVars.playlist.getFile(0,True)
            if get[0] != None:
                globalVars.eventProcess.play(get)
        else: #再生終了後に次がなければ停止とする
            if globalVars.play.getChannelState() == player.state.STOPED:
                globalVars.eventProcess.stop()
    else:
        globalVars.eventProcess.play(get)
