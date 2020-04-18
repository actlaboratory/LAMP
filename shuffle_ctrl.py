import random
import globalVars

#シャッフルコントロール（プレイリストオブジェクト）
class shuffle():
    def __init__(self, list):
        self.list = list #シャッフルする元オブジェクト
        self.history = [] #再生履歴

    def previous(self):
        # プレイリスト再生中であれば
        get = self.getNow()
        if get[1] == globalVars.eventProcess.playingDataNo or get[1] == None:
            #1曲前を再生
            get = self.getPrevious()
            if get[0] != None:
                globalVars.eventProcess.play(get)
        elif get[0] != None:
            # キューなどからの復帰
            globalVars.eventProcess.play(get)

    def next(self):
        # キューを確認
        get = globalVars.queue.getNext()
        if get[0] == None:
            # キューが空の時はシャッフルを進める
            get = self.getNext()
            if get[0] != None:
                globalVars.eventProcess.play(get)
            else: #再生終了後に次がなければ停止とする
                if globalVars.play.getChannelState() == player.state.STOPED:
                    globalVars.eventProcess.stop()
        else:
            globalVars.eventProcess.play(get)

    def getNow(self):
        if len(self.history) == 0:
            return (None, None)
        else:
            return self.history[-1]

    def getPrevious(self):
        if len(self.history) <= 1:
            return (None, None)
        else:
            self.history.pop(-1)
            return self.history[-1]

    def getNext(self):
        if len(self.list.lst) == 0:
            return (None, None)
        else:
            rtn = random.choice(self.list.lst)
            self.history.append(rtn)
            return rtn