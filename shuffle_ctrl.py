# shuffle controler for LAMP
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import random, math
import globalVars, constants, listManager, errorCodes

#シャッフルコントロール（プレイリストオブジェクト）
class shuffle():
    def __init__(self, list):
        self.list = list #シャッフルする元オブジェクト
        self.history = [] #再生履歴
        self.playIndex = -1

    def previous(self, lstConstant):
        # プレイリスト再生中であれば
        if lstConstant == constants.PLAYLIST:
            #1曲前を再生
            if self.playIndex <= 0:
                return errorCodes.END
            else:
                self.playIndex -= 1
                if self.history[self.playIndex] in self.list:
                    self.list.setPointer(self.list.index(self.history[self.playIndex]))
                    return globalVars.eventProcess.play()
                else:
                    self.history.pop(self.playIndex)
                    self.previous(lstConstant)
        else:
            # キューなどからの復帰
            if self.history[self.playIndex] in self.list:
                self.list.setPointer(self.list.index(self.history[self.playIndex]))
                return globalVars.eventProcess.play()
            else:
                self.history.pop(self.playIndex)
                self.previous(constants.PLAYLIST)

    def next(self):
        # キューを確認
        t = globalVars.app.hMainView.queueView.get()
        if t != None: return globalVars.eventProcess.play(constants.QUEUE)
        # キューが空の時はシャッフルを進める
        self.playIndex += 1
        if self.playIndex < len(self.history):
            if self.history[self.playIndex] in self.list:
                self.list.setPointer(self.list.index(self.history[self.playIndex]))
                return globalVars.eventProcess.play()
            else:
                self.next()
        else:
            if len(self.list) == 0: return errorCodes.END
            else:
                rnd = math.floor(random.random() * len(self.list))
                self.list.setPointer(rnd)
                if globalVars.eventProcess.play():
                    self.history.append(self.list[rnd])
                    return True
                else: return False

