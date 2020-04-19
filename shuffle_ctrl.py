import random
import globalVars

#シャッフルコントロール（プレイリストオブジェクト）
class shuffle():
    def __init__(self, list):
        self.list = list #シャッフルする元オブジェクト
        self.history = [] #再生履歴
        self.playIndex = 0

    def previous(self):
        # プレイリスト再生中であれば
        get = self.getNow()
        if get[1] == globalVars.eventProcess.playingDataNo or get[1] == None:
            #1曲前を再生
            get = self.getPrevious()
            globalVars.eventProcess.play(globalVars.playlist, get)
        elif get[0] != None:
            # キューなどからの復帰
            globalVars.eventProcess.play(globalVars.playlist, get)

    def next(self):
        # キューを確認
        get = globalVars.queue.getNext()
        if get[0] == None:
            # キューが空の時はシャッフルを進める
            get = self.getNext()
            if get[0] != None:
                globalVars.eventProcess.play(globalVars.playlist, get)
            else: #再生終了後に次がなければ停止とする
                if globalVars.play.getChannelState() == player.state.STOPED:
                    globalVars.eventProcess.stop()
        else: #キューの再生
            globalVars.eventProcess.play(globalVars.queue, get)

    def getNow(self):
        if len(self.history) == 0:
            return (None, None)
        else:
            return self.history[self.playIndex]

    def getPrevious(self):
        if len(self.list.lst) == 0:
            return (None, None)
        elif self.playIndex == 0:
            rtn = random.choice(self.list.lst)
            self.history.insert(0, rtn)
            return rtn
        else:
            self.playIndex -= 1
            return self.history[self.playIndex]

    def getNext(self):
        if len(self.history) == 0 and self.playIndex == 0: #初期の場合
            self.playIndex = -1
        if len(self.list.lst) == 0:
            rtn = (None, None)
        elif self.playIndex == len(self.history)-1:
            rtn = random.choice(self.list.lst)
            self.history.append(rtn)
        else:
            self.playIndex += 1
            rtn = self.history[self.playIndex]
        return rtn
