# lampControllerCommunicator
# Copyright (C) 2021 Hiroki Fujii <hfujii@hisystron.com>

import os
import win32api
import threading
import pickle
import time
import json
import wx
import requests
import constants
import globalVars
import listManager
from soundPlayer.constants import *
from views import netController


class lampController(threading.Thread):
    def __init__(self):
        # 定数
        self.TITLE = 0
        self.PATH = 1
        self.ARTIST = 2
        self.ALBUM = 3
        self.ALBUM_ARTIST = 4
        self.LENGTH = 5
        
        # フォルダ一覧読み込み
        if not os.path.isfile("netDirList.dat"):
            self.netDirDict = {}
            self.saveDirDict()
        else:
            f = open("netDirList.dat", "rb")
            self.netDirDict = pickle.load(f)
            f.close()
        
        self.fileInfo = ["", "", "", "", "", 0]
        self.exitFlag = False
        self.requestFlag = True
        self.playbackTime = 0
        super().__init__()

    def run(self):
        sleep = constants.API_DEFAULT_INTERVAL
        while not self.exitFlag:
            time.sleep(sleep)
            if self.exitFlag: break
            if not self.requestFlag: continue
            if not globalVars.app.config.getboolean("network","ctrl_client",True): continue
            try:
                responseObject = requests.post(constants.API_COMUNICATION_URL, json=self.makeData(), timeout=5)
                responseObject.encoding="utf-8"
                resJson = responseObject.json()
                sleep = int(resJson["apiSecInterval"])
                for o in resJson["operation"]:
                    if o == "play": wx.CallAfter(globalVars.eventProcess.playButtonControl)
                    elif o == "previous": wx.CallAfter(globalVars.eventProcess.previousBtn)
                    elif o == "next": wx.CallAfter(globalVars.eventProcess.nextFile, True)
                    elif o == "stop": wx.CallAfter(globalVars.eventProcess.stop)
                    elif o == "volumeUp": wx.CallAfter(globalVars.eventProcess.changeVolume, 5)
                    elif o == "volumeDown": wx.CallAfter(globalVars.eventProcess.changeVolume, -5)
                    elif o == "repeatLoop": globalVars.eventProcess.repeatLoopCtrl()
                    elif o == "shuffle": globalVars.eventProcess.shuffleSw()
                    elif o == "clearAllLists": globalVars.eventProcess.clearAllLists()
                    elif "file/" in o or "playlist/" in o:
                        self.__fileProcess(o)
            except Exception as e:
                pass

    def saveDirDict(self):
        f = open("netDirList.dat", "wb")
        pickle.dump(self.netDirDict, f)
        f.close()
    
    # コントローラ表示
    def showController(self):
        d = netController.show()
        if d == wx.ID_CLOSE: self.requestFlag = False
        elif d == wx.ID_OPEN: self.requestFlag = True
        return
    
    def exit(self):
        self.exitFlag = True
    
    def makeData(self):
        if globalVars.play.getStatus() == PLAYER_STATUS_PLAYING: playStatus = "playing"
        elif globalVars.play.getStatus() == PLAYER_STATUS_PAUSED: playStatus = "paused"
        else: playStatus = "stopped"
        userName = globalVars.app.config.getstring("network", "user_name")
        softwareKey = globalVars.app.config.getstring("network", "software_key")
        # リピートループ
        if globalVars.eventProcess.repeatLoopFlag == 0: repeatLoop = "off"
        elif globalVars.eventProcess.repeatLoopFlag == 1: repeatLoop = "repeat"
        elif globalVars.eventProcess.repeatLoopFlag == 2: repeatLoop = "loop"
        else: repeatLoop = ""
        # シャッフル
        if globalVars.eventProcess.shuffleCtrl == None: shuffle = "off"
        else: shuffle = "on"

        jData = {}
        jData["apiVersion"] = 1
        jData["authentication"] = {"userName": userName, "softwareKey": softwareKey}
        jData["software"] = {
            "driveSerialNo": win32api.GetVolumeInformation(os.environ["SystemRoot"][:3])[1],
            "pcName": os.environ["COMPUTERNAME"]
        }
        jData["status"] = {
            "playbackStatus": playStatus,
            "repeatLoop": repeatLoop,
            "shuffle": shuffle,
            "fileTitle": self.fileInfo[self.TITLE],
            "filePath": self.fileInfo[self.PATH],
            "fileArtist": self.fileInfo[self.ARTIST],
            "fileAlbum": self.fileInfo[self.ALBUM],
            "fileAlbumArtist": self.fileInfo[self.ALBUM_ARTIST],
            "playbackTime": self.__getPlaybackTime(),
            "fileLength": self.fileInfo[self.LENGTH]
        }
        return jData
    
    def setFileInfo(self):
        if globalVars.eventProcess.playingList == constants.PLAYLIST: t = listManager.getTuple(constants.PLAYLIST)
        else: t = globalVars.listInfo.playingTmp
        if t[constants.ITEM_TITLE] == "": self.fileInfo = [t[constants.ITEM_NAME]]
        else: self.fileInfo = [t[constants.ITEM_TITLE]]
        self.fileInfo += [t[constants.ITEM_PATH],
            t[constants.ITEM_ARTIST], t[constants.ITEM_ALBUM], t[constants.ITEM_ALBUMARTIST]]
        if t[constants.ITEM_LENGTH] == None: self.fileInfo.append(0)
        else: self.fileInfo.append(t[constants.ITEM_LENGTH])

    def clearFileInfo(self):
        self.fileInfo = ["", "", "", "", "", 0]

    def __getPlaybackTime(self):
        ret = self.playbackTime
        self.playbackTime = 0
        return ret

    def setPlaybackTime(self, sec):
        if (isinstance(sec, int) or isinstance(sec, float)) and sec >= 0:
            self.playbackTime = int(sec)
        else: self.playbackTime = 0

    def __fileProcess(self, resString):
        l = resString.split("/")
        if (not l[0] in ["file", "playlist"]) or not (len(l)>=2 and l[1] in self.netDirDict): return
        # ローカル用パスを構成
        path = os.path.join(self.netDirDict[l[1]], "\\".join(l[2:]))
        if l[0] == "file": wx.CallAfter(globalVars.eventProcess.forcePlay, path)
        elif l[0] == "playlist": wx.CallAfter(listManager.addItems, [path], globalVars.app.hMainView.playlistView, id=--1, ignoreError=True)
