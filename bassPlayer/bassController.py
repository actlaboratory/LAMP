import sys, ctypes, os, threading, time
from .bass import pybass
from .bass import bassFx
from .bass import bassHls
from .bass import pytags
from .constants import *

# ロックオブジェクト
lock = threading.Lock()

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

def bassInit(playerID):
    """BASS初期化要求（playerID） => bool """
    return _send(playerID, PLAYER_SEND_INIT)

def bassFree(playerID):
    """デバイスのフリーと再生情報一時保存要求（playerID） """
    _send(playerID, PLAYER_SEND_FREE)

def kill(playerID):
    """bassスレッド終了（playerID）"""
    if  _playerList[playerID] != None:
        _memory[playerID][M_STATUS] = PLAYER_SEND_KILL
        _playerList[playerID] = None

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
    _send(playerID, PLAYER_SEND_REPEAT, boolVal)

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
        self.__autoChange = []
        self.__positionTmp = []
        self.__eofFlag = []
        self.__repeat = []
        self.__sourceType = []
        self.__playingFlag = []
        self.__handle = []
        self.__reverseHandle = []
        self.__freq = []
        self.__device = []

    def setNewPlayer(self):
        self.__autoChange.append(True)
        self.__positionTmp.append(-1)
        self.__eofFlag.append(False)
        self.__repeat.append(False)
        self.__sourceType.append(PLAYER_SOURCETYPE_NUL)
        self.__playingFlag.append(False)
        self.__handle.append(0)
        self.__reverseHandle.append(0)
        self.__freq.append(0)
        self.__device.append(0)

    def __reset(self, id):
        self.__playingFlag[id] = False
        self.__handle[id] = 0
        self.__reverseHandle[id] = 0
        self.__freq[id] = 0
    
    def run(self):
        while True:
            time.sleep(0.02)
            for id in range(len(_playerList)):
                # 通信
                sRet = -1
                s = _memory[id][M_STATUS]
                if s == PLAYER_SEND_INIT:
                    if self.bassInit(id):sRet = 1
                elif s == PLAYER_SEND_NEWPLAYER:
                    self.setNewPlayer()
                    sRet = 1
                elif s == PLAYER_SEND_FREE:
                    if self.bassFree(id):sRet = 1
                elif s == PLAYER_SEND_KILL:
                    self.__del__()
                    return
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
                elif s == PLAYER_SEND_REPEAT:
                    self.__repeat[id] = _memory[id][M_VALUE]
                    sRet = 1
                elif s == PLAYER_SEND_SETHLSDELAY:
                    if pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY, _memory[id][M_VALUE]): sRet = 1
                elif s == PLAYER_SEND_AUTOCHANGE:
                    self.__autoChange[id] = _memory[id][M_VALUE]
                    sRet = 1
                else: sRet = 0
                
                if sRet == 1: _memory[id][M_STATUS] = PLAYERSTATUS_STATUS_OK
                elif sRet == -1: _memory[id][M_STATUS] = PLAYERSTATUS_STATUS_FAILD

                # 再生監視
                a = pybass.BASS_ChannelIsActive(self.__handle[id])
                if a == pybass.BASS_ACTIVE_PAUSED_DEVICE: 
                    self.__autoChangeDevice(id)
                elif a == pybass.BASS_ACTIVE_STALLED or (a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag[id] and self.__sourceType[id] == PLAYER_SOURCETYPE_STREAM):
                    if not self.play(id):
                        self.stop(id)
                        self.__eofFlag[id] == True
                elif a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag[id] and self.__sourceType[id] == PLAYER_SOURCETYPE_FILE:
                    if pybass.BASS_ChannelGetPosition(self.__handle[id], pybass.BASS_POS_BYTE) == pybass.BASS_ChannelGetLength(self.__handle[id], pybass.BASS_POS_BYTE) != -1:
                        if self.__repeat[id]: self.play(id)
                        else:
                            self.stop(id)
                            self.__eofFlag[id] = True
        return

    def bassInit(self, id, selfCall=False):
        """ bass.dll初期化(id, bool 内部呼び出し) => bool """
        pybass.BASS_SetDevice(id)
        pybass.BASS_Free()
        ret = False
        if selfCall: device = PLAYER_DEFAULT_SPEAKER
        else: device = _playerList[id].getConfig(PLAYER_CONFIG_DEVICE)
        if device == PLAYER_DEFAULT_SPEAKER:
            ret = pybass.BASS_Init(-1, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        elif device == PLAYER_ANY_SPEAKER:
            for i in range(len(getDeviceList()) - 1):
                if pybass.BASS_Init(i + 1, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0):
                    ret = True
                    break
        elif device == PLAYER_NO_SPEAKER:
            ret = pybass.BASS_Init(0, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        else:
            ret = pybass.BASS_Init(device, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        if ret and self.__playingFlag[id]: self.reStartPlay()
        if ret: self.__device[id] = pybass.BASS_GetDevice()
        return ret

    def __del__(self):
        for d in self.__device:
            pybass.BASS_SetDevice(d)
            pybass.BASS_Free()
    
    
    def __autoChangeDevice(self, id):
        self.bassFree(id)
        if self.__autoChange: self.__reset(id)
        
    def bassFree(self, id):
        """ 再生位置を保存してデバイスをFree（id） """
        pybass.BASS_SetDevice(self.__device[id])
        posBTmp = pybass.BASS_ChannelGetPosition(self.__handle[id], pybass.BASS_POS_BYTE)
        if posBTmp != -1: self.__positionTmp[id] = pybass.BASS_ChannelBytes2Seconds(self.__handle[id], posBTmp)
        else: self.__positionTmp[id] = -1
        pybass.BASS_Free()
        
    def reStartPlay(self, id):
        """ 再生復旧（id） => bool """
        if _playerList[id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_PATH:
            self.createHandle(id)
        elif _playerList[id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_URL:
            self.createHandleFromURL(id)
        if self.__positionTmp[id] != -1:
            posB = pybass.BASS_ChannelSeconds2Bytes(self.__handle[id], self.__positionTmp)
            pybass.BASS_ChannelSetPosition(self.__handle[id], posB, pybass.BASS_POS_BYTE)
        return self.play(id)

    
    def createHandle(self, id):
        """ ハンドル作成（id） => bool """
        pybass.BASS_SetDevice(self.__device[id])
        self.stop(id)
        self.__eofFlag[id] = False
        self.__playingFlag[id] = False
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
        self.__playingFlag[id] = False
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
        if ret: self.__playingFlag[id] = True
        else: self.__playingFlag[id] = False
        return ret

    def pause(self, id):
        """ 一時停止（id） => bool """
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        return pybass.BASS_ChannelPause(self.__handle[id])

    def stop(self, id):
        """ 停止（id） => bool """
        pybass.BASS_StreamFree(self.__handle[id])
        self.__reset(id)
        return True

    def getStatus(self, id):
        """ ステータス取得（id） => True"""
        if pybass.BASS_GetDevice() == 4294967295: # -1のこと
            _memory[id][M_VALUE] = PLAYER_STATUS_DEVICEERROR
            return True
        elif self.__playingFlag[id] and pybass.BASS_ChannelIsActive(self.__handle[id]) == pybass.BASS_ACTIVE_PLAYING:
            _memory[id][M_VALUE] = PLAYER_STATUS_PLAYING
        elif self.__eofFlag[id]: _memory[id][M_VALUE] = PLAYER_STATUS_END
        elif pybass.BASS_ChannelIsActive(self.__handle[id]) == pybass.BASS_ACTIVE_PAUSED: _memory[id][M_VALUE] = PLAYER_STATUS_PAUSED
        elif self.__playingFlag[id]: _memory[id][M_VALUE] = PLAYER_STATUS_LOADING
        else: _memory[id][M_VALUE] = PLAYER_STATUS_STOPPED
        return True


    def setSpeed(self, id):
        """ 再生速度設定（id） => bool"""
        if self.__sourceType[id] != PLAYER_SOURCETYPE_FILE: return False
        speed = _playerList[id].getConfig(PLAYER_CONFIG_SPEED)
        return pybass.BASS_ChannelSetAttribute(self.__handle[id],bassFx.BASS_ATTRIB_TEMPO, speed)

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
        return pybass.BASS_ChannelSetAttribute(self.__handle[id], pybass.BASS_ATTRIB_VOL, vol)

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

# bassスレッド生成
player = bassThread()
player.start()
