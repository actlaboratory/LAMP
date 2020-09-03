import sys, ctypes, os, threading, time, winsound
from .bass import pybass
from .bass import bassFx
from .bass import bassHls
from .bass import pytags
from .constants import *

# ロックオブジェクト
lock = threading.Lock()

# プレイヤースレッド
_playerThread = None

# デバイスリスト
_deviceList = []

# プレイヤーオブジェクトのリスト
_playerList = []

# ハンドルの辞書
_memory = []
M_STATUS = 0
M_VALUE = 1


def connectPlayer(playerObject):
    """
    プレイヤーと接続(playerオブジェクト) => int PlayerID
    プレイヤーオブジェクトに対して固有のIDを発行し、設定情報を連携する、
    """
    global _playerThread
    global _playerList
    global _memory
    if _playerThread == None or _playerThread.isAlive() == False: # bassスレッド再生成
        _playerList = []
        _memory = []
        _playerThread = bassThread()
        _playerThread.start()
    try:
        index = _playerList.index(None)
        _playerList[index] = playerObject
        _memory[index] = [PLAYERSTATUS_STATUS_OK, 0]
    except ValueError:
        _playerList.append(playerObject)
        index = len(_playerList) - 1
        _memory.append([PLAYERSTATUS_STATUS_OK, 0])
    _send(index, PLAYER_SEND_NEWPLAYER)
    return index

def getDeviceList():
    """
    デバイスリストを取得 => list
    無効なデバイスはNoneを格納
    """
    p = pybass.BASS_DEVICEINFO()
    newList = []
    index = 0
    while pybass.BASS_GetDeviceInfo(index, p):
        if p.flags and pybass.BASS_DEVICE_ENABLED: newList.append(p.name.decode("shift-jis"))
        else: newList.append(None)
        index += 1
    for i in range(len(_deviceList), len(newList)):
        _deviceList.append(newList[i])
    return _deviceList
getDeviceList()

def getDefaultDevice():
    """ デフォルトデバイス返却 => int """
    p = pybass.BASS_DEVICEINFO()
    index = 1
    while pybass.BASS_GetDeviceInfo(index, p):
        if p.flags & pybass.BASS_DEVICE_DEFAULT: return index
        else: index += 1
    return 0

def isInitialized(device):
    """ init済みならTrue => bool """
    p = pybass.BASS_DEVICEINFO()
    pybass.BASS_GetDeviceInfo(device, p)
    return p.flags & pybass.BASS_DEVICE_INIT > 0

def bassInit(playerID):
    """BASS初期化要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_INIT)

def changeDevice(playerID):
    """デバイス変更要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_DEVICE)


def bassFree(playerID):
    """デバイスのフリーと再生情報一時保存要求（playerID） """
    _send(playerID, PLAYER_SEND_FREE)

def exitPlayer(playerID):
    """プレイヤー終了（playerID）"""
    _send(playerID, PLAYER_SEND_EXIT)

def setAutoChangeDevice(playerID, bool):
    """ デバイス自動切り替え（bool） """
    _send(playerID, PLAYER_SEND_AUTOCHANGE, bool)

def setNetTimeout(playerID, miliSec):
    """ ネットワークタイムアウトを設定（playerID, int ミリ秒） => bool """
    return _send(playerID, PLAYER_SEND_SETNETTIMEOUT, miliSec)

def setHlsDelay(playerID, sec):
    """ HLS遅延設定要求（playerID, int 秒） => bool """
    return _send(playerID, PLAYER_SEND_SETHLSDELAY, sec)

def setFile(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_FILE)

def setURL(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_URL)

def setRepeat(playerID, boolVal):
    """ リピート（bool） """
    _send(playerID, PLAYER_SEND_SETREPEAT, boolVal)

def getRepeat(playerID):
    """ リピート取得（id） """
    return _send(playerID, PLAYER_SEND_GETREPEAT)

def play(playerID):
    """ 再生(playerID) => bool """
    return _send(playerID, PLAYER_SEND_PLAY)

def pause(playerID):
    """ 一時停止(playerID) => bool """
    return _send(playerID, PLAYER_SEND_PAUSE)

def stop(playerID):
    """ 停止(playerID) => bool """
    return _send(playerID, PLAYER_SEND_STOP)

def getStatus(playerID):
    """ ステータス取得要求(playerID) => ステータス定数 または None """
    return _send(playerID, PLAYER_SEND_GETSTATUS, None, True)

def setSpeed(playerID):
    """ 再生速度変更要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_SPEED)

def setKey(playerID):
    """ 再生キー変更要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_KEY)

def setFreq(playerID):
    """ 再生周波数変更要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_FREQ)

def setVolume(playerID):
    """ 再生音量変更要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_VOLUME)

def getPosition(playerID):
    """
    再生位置取得要求（playerID） => int 秒数
    失敗した場合は-1を返却
    """
    return _send(playerID, PLAYER_SEND_GETPOSITION, None, True, True)

def setPosition(playerID, second):
    """ 再生位置設定要求（playerID, int 秒数） => bool """
    return _send(playerID, PLAYER_SEND_SETPOSITION, second)

def getLength(playerID):
    """ 合計時間取得要求（playerID）=> int 秒数 """
    return _send(playerID, PLAYER_SEND_GETLENGTH, None, True, True)

def _send(playerID, status, value=None, returnValue=False, falseToInt=False):
    """ 要求を受け付けて処理が終わるまで待機（playerID, ステータス, バリュー, バリューを返却?, Falseを-1で返却?） => 結果 """
    with lock:
        if value != None: _memory[playerID][M_VALUE] = value
        _memory[playerID][M_STATUS] = status
        while True:
            time.sleep(0.02)
            if _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_OK:
                if returnValue: return _memory[playerID][M_VALUE]
                else: return True
            elif _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_FAILD:
                if falseToInt: return -1
                else: return False

class bassThread(threading.Thread):
    def __init__(self):
        super().__init__()
        # プラグイン適用
        pybass.BASS_PluginLoad(b"basshls.dll", 0)
        pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY,10)
        pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_BUFFER, 200000)
        pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_PREBUF, 1)
        pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_READTIMEOUT, 10000)
        pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_TIMEOUT, 10000)

        # 初期化
        self.__defaultDevice = []
        self.__autoChange = []
        self.__positionTmp = []
        self.__eofFlag = []
        self.__repeat = []
        self.__sourceType = []

        self.__playingFlag = []
        # >>> playingFlag定数
        self.PLAYINGF_STOP = 0
        self.PLAYINGF_PAUSE = 1
        self.PLAYINGF_PLAY = 2

        self.__handle = []
        self.__reverseHandle = []
        self.__freq = []
        self.__device = []

    def setNewPlayer(self, id):
        """新しいプレイヤーをセット"""
        if id == len(_playerList) - 1:
            self.__autoChange.append(False)
            self.__positionTmp.append(-1)
            self.__eofFlag.append(False)
            self.__repeat.append(False)
            self.__sourceType.append(PLAYER_SOURCETYPE_NUL)
            self.__playingFlag.append(self.PLAYINGF_STOP)
            self.__handle.append(0)
            self.__reverseHandle.append(0)
            self.__freq.append(0)
            self.__device.append(0)
            self.__defaultDevice.append(False)
        else:
            self.__autoChange[id] = False
            self.__positionTmp[id] = -1
            self.__eofFlag[id] = False
            self.__repeat[id] = False
            self.__sourceType[id] = PLAYER_SOURCETYPE_NUL
            self.__playingFlag[id] = self.PLAYINGF_STOP
            self.__handle[id] = 0
            self.__reverseHandle[id] = 0
            self.__freq[id] = 0
            self.__device[id] = 0
            self.__defaultDevice[id] = False

    def exitPlayer(self, id):
        """プレイヤー終了（id）"""
        self.stop(id)
        self.__autoChange[id] = None
        self.__positionTmp[id] = None
        self.__eofFlag[id] = None
        self.__repeat[id] = None
        self.__sourceType[id] = None
        self.__playingFlag[id] = self.PLAYINGF_STOP
        self.__handle[id] = 0
        self.__reverseHandle[id] = 0
        self.__freq[id] = None
        self.__device[id] = None
        self.__defaultDevice[id] = None
        _playerList[id] = None

    def __reset(self, id):
        self.__handle[id] = 0
        self.__reverseHandle[id] = 0
        self.__freq[id] = 0
    
    def run(self):
        while True:
            time.sleep(0.02)
            # スレッドの自動終了
            threadEnd = False
            for o in _playerList:
                if o == None: threadEnd = True
                else:
                    threadEnd = False
                    break
            if threadEnd:
                return
            
            for id in range(len(_playerList)):
                # 終了プレイヤースキップ
                if _playerList[id] == None: continue
                
                # 通信
                sRet = -1
                s = _memory[id][M_STATUS]
                if s == PLAYER_SEND_NEWPLAYER:
                    self.setNewPlayer(id)
                    sRet = 1
                elif s == PLAYER_SEND_INIT:
                    if self.bassInit(id):sRet = 1
                elif s == PLAYER_SEND_DEVICE:
                    self.__changeDevice(id, True)
                    sRet = 1
                elif s == PLAYER_SEND_FREE:
                    if self.bassFree(id):sRet = 1
                elif s == PLAYER_SEND_EXIT:
                    self.exitPlayer(id)
                    sRet = 1
                elif s == PLAYER_SEND_FILE:
                    if self.createHandle(id): sRet = 1
                elif s == PLAYER_SEND_URL:
                    if self.createHandleFromURL(id): sRet = 1
                elif s == PLAYER_SEND_PLAY:
                    if self.play(id): sRet = 1
                elif s == PLAYER_SEND_PAUSE:
                    if self.pause(id): sRet = 1
                elif s == PLAYER_SEND_GETSTATUS:
                    if self.getStatus(id): sRet = 1
                elif s == PLAYER_SEND_SPEED:
                    if self.setSpeed(id): sRet = 1
                elif s == PLAYER_SEND_KEY:
                    if self.setKey(id): sRet = 1
                elif s == PLAYER_SEND_FREQ:
                    if self.setFreq(id): sRet = 1
                elif s == PLAYER_SEND_VOLUME:
                    if self.setVolume(id): sRet = 1
                elif s == PLAYER_SEND_GETPOSITION:
                    if self.getPosition(id): sRet = 1
                elif s == PLAYER_SEND_SETPOSITION:
                    if self.setPosition(id): sRet = 1
                elif s == PLAYER_SEND_GETLENGTH:
                    if self.getLength(id): sRet = 1
                elif s == PLAYER_SEND_STOP:
                    if self.stop(id): sRet = 1
                # 設定
                elif s == PLAYER_SEND_SETNETTIMEOUT:
                    pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_TIMEOUT, _memory[id][M_VALUE])
                    pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_READTIMEOUT, _memory[id][M_VALUE])
                    sRet = 1
                elif s == PLAYER_SEND_SETREPEAT:
                    self.__repeat[id] = _memory[id][M_VALUE]
                    sRet = 1
                elif s == PLAYER_SEND_GETREPEAT:
                    if repeat[id]: sRet = 1
                elif s == PLAYER_SEND_SETHLSDELAY:
                    if pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY, _memory[id][M_VALUE]): sRet = 1
                elif s == PLAYER_SEND_AUTOCHANGE:
                    self.__autoChange[id] = _memory[id][M_VALUE]
                    sRet = 1
                else: sRet = 0
                
                if sRet == 1: _memory[id][M_STATUS] = PLAYERSTATUS_STATUS_OK
                elif sRet == -1: _memory[id][M_STATUS] = PLAYERSTATUS_STATUS_FAILD

                # プレイヤー終了検知
                if _playerList[id] == None: continue
                
                # 再生監視
                if self.__defaultDevice[id] and (self.__device[id] != getDefaultDevice()):
                    self.__changeDevice(id, True)
                a = pybass.BASS_ChannelIsActive(self.__handle[id])
                if a == pybass.BASS_ACTIVE_PAUSED_DEVICE: 
                    self.__changeDevice(id)
                    self.__device[id] = 0
                elif a == pybass.BASS_ACTIVE_STALLED or (a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag[id] == self.PLAYINGF_PLAY and self.__sourceType[id] == PLAYER_SOURCETYPE_STREAM):
                    if not self.play(id):
                        self.stop(id)
                        self.__eofFlag[id] == True
                elif a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag[id] > self.PLAYINGF_STOP and self.__sourceType[id] == PLAYER_SOURCETYPE_FILE:
                    if pybass.BASS_ChannelGetPosition(self.__handle[id], pybass.BASS_POS_BYTE) == pybass.BASS_ChannelGetLength(self.__handle[id], pybass.BASS_POS_BYTE) != -1:
                        if self.__repeat[id]: self.play(id)
                        else:
                            self.stop(id)
                            self.__eofFlag[id] = True
        return

    def bassInit(self, id):
        """ bass.dll初期化(id) => bool """
        ret = False
        device = _playerList[id].getConfig(PLAYER_CONFIG_DEVICE)
        self.__defaultDevice[id] = False
        if device == PLAYER_DEFAULT_SPEAKER:
            device = getDefaultDevice()
            self.__defaultDevice[id] = True
        if device > 0:
            if isInitialized(device):
                ret = pybass.BASS_SetDevice(device)
                pybass.BASS_Start()
                self.__device[id] = device
            elif pybass.BASS_Init(device, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0):
                self.__device[id] = device
                ret = True
        if not ret:
            self.__device[id] = 0
        return ret

    def __del__(self):
        for d in self.__device:
            if d != None:
                pybass.BASS_SetDevice(d)
                pybass.BASS_Free()
    
    
    def __changeDevice(self, id, forChannel=False):
        """ デバイス変更（ID, チャネル単体?）=> bool """
        self.backup()
        if not forChannel: self.bassFree(id)
        else: pybass.BASS_StreamFree(self.__handle[id])
        self.__reset(id)
        deviceTmp = self.__device[id]
        if forChannel:
            if self.bassInit(id):
                ret = True
                if self.__playingFlag[id] > self.PLAYINGF_STOP: self.reStartPlay(id)
            else:
                ret = False
        else:
            ret = False
            for i in range(len(_playerList)):
                if not self.__autoChange[id] and not self.__defaultDevice[id]: continue
                if deviceTmp == self.__device[i]:
                    self.bassInit(i)
                    if self.__playingFlag[id] > self.PLAYINGF_STOP:
                        self.reStartPlay(i)
                ret = True
        return ret
        
    def bassFree(self, id):
        """ BASS Free（id） => bool """
        if not pybass.BASS_SetDevice(self.__device[id]): return False
        return pybass.BASS_Free()

    def backup(self):
        """ 再生位置を保存 """
        for i in range(len(_playerList)):
            posBTmp = pybass.BASS_ChannelGetPosition(self.__handle[i], pybass.BASS_POS_BYTE)
            if posBTmp != -1: self.__positionTmp[i] = pybass.BASS_ChannelBytes2Seconds(self.__handle[i], posBTmp)
        
    def reStartPlay(self, id):
        """ 再生復旧（id）"""
        pause = False
        if self.__playingFlag[id] == self.PLAYINGF_PAUSE: pause = True
        if _playerList[id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_PATH: self.createHandle(id)
        elif _playerList[id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_URL: self.createHandleFromURL(id)
        if self.__positionTmp[id] != -1:
            posB = pybass.BASS_ChannelSeconds2Bytes(self.__handle[id], self.__positionTmp[id])
            pybass.BASS_ChannelSetPosition(self.__handle[id], posB, pybass.BASS_POS_BYTE)
            if not pause: self.play(id)

    def createHandle(self, id):
        """ ハンドル作成（id） => bool """
        pybass.BASS_SetDevice(self.__device[id])
        self.stop(id)
        self.__eofFlag[id] = False
        self.__playingFlag[id] = self.PLAYINGF_STOP
        source = _playerList[id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateFile(False,source, 0, 0, pybass.BASS_UNICODE | pybass.BASS_STREAM_PRESCAN | pybass.BASS_STREAM_DECODE)
        reverseHandle = bassFx.BASS_FX_ReverseCreate(handle,0.3,bassFx.BASS_FX_FREESOURCE | pybass.BASS_STREAM_DECODE)
        handle = bassFx.BASS_FX_TempoCreate(handle,0)
        pybass.BASS_ChannelSetAttribute(reverseHandle,bassFx.BASS_ATTRIB_REVERSE_DIR,bassFx.BASS_FX_RVS_FORWARD)
        if handle and reverseHandle:
            # サンプリングレートを読み込み
            cFreq = ctypes.c_float()
            pybass.BASS_ChannelGetAttribute(handle, pybass.BASS_ATTRIB_FREQ, cFreq)
            self.__handle[id] = handle
            self.__reverseHandle[id] = reverseHandle
            self.__freq[id] = round(cFreq.value)
            self.__sourceType[id] = PLAYER_SOURCETYPE_FILE
            self.__setChannelConfig(id)
            return True
        else: return False

    def createHandleFromURL(self, id):
        """ URLからハンドル作成（id） => bool """
        pybass.BASS_SetDevice(self.__device[id])
        self.stop(id)
        self.__eofFlag[id] = False
        self.__playingFlag[id] = self.PLAYINGF_STOP
        source = _playerList[id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateURL(source.encode(), 0, 0, 0, 0)
        if handle:
            self.__handle[id] = handle
            self.__reverseHandle[id] = 0
            self.__freq[id] = 0
            if pybass.BASS_ChannelGetPosition(self.__handle[id], pybass.BASS_POS_BYTE) <= 0: self.__sourceType[id] = PLAYER_SOURCETYPE_STREAM
            else: self.__sourceType[id] = PLAYER_SOURCETYPE_FILE
            self.__setChannelConfig(id)
            return True
        else: return False

    def __setChannelConfig(self, id):
        """ チャネル固有設定適用 """
        self.setVolume(id)
        self.setSpeed(id)
        self.setKey(id)
        self.setFreq(id)
    
    def play(self, id):
        """ 再生（id）=> bool  """
        ret = pybass.BASS_ChannelPlay(self.__handle[id], False)
        if ret: self.__playingFlag[id] = self.PLAYINGF_PLAY
        else:
            if pybass.BASS_ErrorGetCode() == pybass.BASS_ERROR_START: self.__device[id] = 0
            else: self.__playingFlag[id] = self.PLAYINGF_STOP
        return ret

    def pause(self, id):
        """ 一時停止（id） => bool """
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        ret =  pybass.BASS_ChannelPause(self.__handle[id])
        if ret: self.__playingFlag[id] = self.PLAYINGF_PAUSE
        return ret

    def stop(self, id):
        """ 停止（id） => bool """
        pybass.BASS_StreamFree(self.__handle[id])
        self.__reset(id)
        self.__playingFlag[id] = self.PLAYINGF_STOP
        self.__eofFlag[id] = False
        return True

    def getStatus(self, id):
        """ ステータス取得（id） => True"""
        if pybass.BASS_GetDevice() == 4294967295 or self.__device[id] == 0:
        # 4294967295 => -1のこと
            _memory[id][M_VALUE] = PLAYER_STATUS_DEVICEERROR
            return True
        elif self.__playingFlag[id] > self.PLAYINGF_STOP and pybass.BASS_ChannelIsActive(self.__handle[id]) == pybass.BASS_ACTIVE_PLAYING:
            _memory[id][M_VALUE] = PLAYER_STATUS_PLAYING
        elif self.__eofFlag[id]: _memory[id][M_VALUE] = PLAYER_STATUS_END
        elif pybass.BASS_ChannelIsActive(self.__handle[id]) == pybass.BASS_ACTIVE_PAUSED or (self.__handle[id] and pybass.BASS_ChannelIsActive(self.__handle[id]) == pybass.BASS_ACTIVE_STOPPED):
            _memory[id][M_VALUE] = PLAYER_STATUS_PAUSED
        elif self.__playingFlag[id] > self.PLAYINGF_STOP: _memory[id][M_VALUE] = PLAYER_STATUS_LOADING
        else: _memory[id][M_VALUE] = PLAYER_STATUS_STOPPED
        return True


    def setSpeed(self, id):
        """ 再生速度設定（id） => bool"""
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        speed = _playerList[id].getConfig(PLAYER_CONFIG_SPEED)
        return pybass.BASS_ChannelSetAttribute(self.__handle[id],bassFx.BASS_ATTRIB_TEMPO, speed - 100)

    def setKey(self, id):
        """ 再生キー設定（id） => bool"""
        key = _playerList[id].getConfig(PLAYER_CONFIG_KEY)
        return pybass.BASS_ChannelSetAttribute(self.__handle[id],bassFx.BASS_ATTRIB_TEMPO_PITCH, key)

    def setFreq(self, id):
        """ 再生周波数設定（id） => bool"""
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        freqArg = _playerList[id].getConfig(PLAYER_CONFIG_FREQ)
        freq = round((freqArg * self.__freq[id]) / 100)
        return pybass.BASS_ChannelSetAttribute(self.__handle[id],bassFx.BASS_ATTRIB_TEMPO_FREQ, freq)

    def setVolume(self, id):
        """ 再生音量設定（id） => bool"""
        vol = _playerList[id].getConfig(PLAYER_CONFIG_AMPVOL)
        return pybass.BASS_ChannelSetAttribute(self.__handle[id], pybass.BASS_ATTRIB_VOL, vol / 100)

    def getPosition(self, id):
        """  再生位置秒数取得（id） => bool (value)"""
        byte = pybass.BASS_ChannelGetPosition(self.__handle[id], pybass.BASS_POS_BYTE)
        if byte != -1:
            sec = pybass.BASS_ChannelBytes2Seconds(self.__handle[id], byte)
            _memory[id][M_VALUE] = sec
            return True
        else: return False

    def setPosition(self, id):
        """ 秒数で再生位置を設定（id） => bool """
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        sec = _memory[id][M_VALUE]
        byte = pybass.BASS_ChannelSeconds2Bytes(self.__handle[id], sec)
        if self.__sourceType[id] == PLAYER_SOURCETYPE_FILE: return pybass.BASS_ChannelSetPosition(self.__handle[id], byte, pybass.BASS_POS_BYTE)
        else: return False

    def getLength(self, id):
        """  合計時間秒数取得（id）=> bool (value)"""
        byte = pybass.BASS_ChannelGetLength(self.__handle[id], pybass.BASS_POS_BYTE)
        if byte != -1:
            sec = pybass.BASS_ChannelBytes2Seconds(self.__handle[id], byte)
            _memory[id][M_VALUE] = sec
        else: _memory[id][M_VALUE] = -1
        return True
