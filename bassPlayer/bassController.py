import sys, ctypes, os, threading, time
from .bass import pybass
from .bass import bassFx
from .bass import bassHls
from .bass import pytags
from .constants import *

# デバイスリスト
_deviceList = []

# プレイヤーオブジェクトのリスト
_playerList = []

# スレッド
__threadList = []

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
    __threadList.append(bassThread(index))
    __threadList[index].start()
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
    _memory[playerID][M_STATUS] = PLAYER_SEND_INIT
    return _waitReturn(playerID)

def bassFree(playerID):
    """デバイスのフリーと再生情報一時保存要求（playerID） """
    _memory[playerID][M_STATUS] = PLAYER_SEND_FREE
    _waitReturn(playerID)

def kill(playerID):
    """bassスレッド終了（playerID）"""
    if  _playerList[playerID] != None:
        _memory[playerID][M_STATUS] = PLAYER_SEND_KILL
        _playerList[playerID] = None

def setAutoChangeDevice(playerID, bool):
    """ デバイス自動切り替え（bool） """
    _memory[playerID][M_VALUE] = bool
    _memory[playerID][M_STATUS] = PLAYER_SEND_AUTOCHANGE
    _waitReturn(playerID)

def setNetTimeout(playerID, miliSec):
    """ ネットワークタイムアウトを設定（playerID, int ミリ秒） => bool """
    _memory[playerID][M_VALUE] = miliSec
    _memory[playerID][M_STATUS] = PLAYER_SEND_SETNETTIMEOUT
    return _waitReturn(playerID)

def setHlsDelay(playerID, sec):
    """ HLS遅延設定要求（playerID, int 秒） => bool """
    _memory[playerID][M_VALUE] = sec
    _memory[playerID][M_STATUS] = PLAYER_SEND_SETHLSDELAY
    return _waitReturn(playerID)

def setFile(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_FILE
    return _waitReturn(playerID)

def setURL(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_URL
    return _waitReturn(playerID)

def setRepeat(playerID, boolVal):
    """ リピート（bool） """
    _memory[playerID][M_VALUE] = boolVal
    _memory[playerID][M_STATUS] = PLAYER_SEND_REPEAT
    _waitReturn(playerID)

def play(playerID):
    """ 再生(playerID) => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_PLAY
    return _waitReturn(playerID)

def pause(playerID):
    """ 一時停止(playerID) => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_PAUSE
    return _waitReturn(playerID)

def stop(playerID):
    """ 停止(playerID) => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_STOP
    return _waitReturn(playerID)

def getStatus(playerID):
    """ ステータス取得要求(playerID) => ステータス定数 または None """
    _memory[playerID][M_STATUS] = PLAYER_SEND_GETSTATUS
    if _waitReturn(playerID): return _memory[playerID][M_VALUE]

def setSpeed(playerID):
    """ 再生速度変更要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_SPEED
    return _waitReturn(playerID)

def setKey(playerID):
    """ 再生キー変更要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_KEY
    return _waitReturn(playerID)

def setFreq(playerID):
    """ 再生周波数変更要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_FREQ
    return _waitReturn(playerID)

def setVolume(playerID):
    """ 再生音量変更要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_VOLUME
    return _waitReturn(playerID)

def getPosition(playerID):
    """
    再生位置取得要求（playerID） => int 秒数
    失敗した場合は-1を返却
    """
    _memory[playerID][M_STATUS] = PLAYER_SEND_GETPOSITION
    if _waitReturn(playerID): return _memory[playerID][M_VALUE]
    else: return -1

def setPosition(playerID, second):
    """ 再生位置設定要求（playerID, int 秒数） => bool """
    _memory[playerID][M_VALUE] = second
    _memory[playerID][M_STATUS] = PLAYER_SEND_SETPOSITION
    return _waitReturn(playerID)

def getLength(playerID):
    """ 合計時間取得要求（playerID）=> int 秒数 """
    _memory[playerID][M_STATUS] = PLAYER_SEND_GETLENGTH
    if _waitReturn(playerID): return _memory[playerID][M_VALUE]
    else: return -1

def _waitReturn(playerID):
    """ 処理が終わるまで待機（playerID） => bool """
    while True:
        time.sleep(0.02)
        if _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_OK:
            return True
        elif _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_FAILD:
            return False

class bassThread(threading.Thread):
    def __init__(self, playerID, streamFree=False):
        if not streamFree:
            super().__init__()
        # プラグイン適用
            pybass.BASS_PluginLoad(b"basshls.dll", 0)
            pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY,10)
            pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_BUFFER, 200000)
            pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_PREBUF, 1)
            pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_READTIMEOUT, 10000)
            pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_TIMEOUT, 10000)

        # 初期化
            self.__autoChange = True
            self.__eofFlag = False
            self.__repeat = False
        self.__id = playerID
        self.__sourceType = PLAYER_SOURCETYPE_NUL
        self.__playingFlag = False
        self.__handle = 0
        self.__reverseHandle = 0
        self.__freq = 0
        self.__positionTmp = -1

    def run(self):
        while True:
            time.sleep(0.02)

            # 通信
            sRet = -1
            s = _memory[self.__id][M_STATUS]
            if s == PLAYER_SEND_INIT:
                if self.bassInit():sRet = 1
            elif s == PLAYER_SEND_FREE:
                if self.bassFree():sRet = 1
            elif s == PLAYER_SEND_KILL:
                self.__del__()
                break
            elif s == PLAYER_SEND_FILE:
                if self.createHandle(): sRet = 1
            elif s == PLAYER_SEND_URL:
                if self.createHandleFromURL(): sRet = 1
            elif s == PLAYER_SEND_PLAY:
                if self.play(): sRet = 1
            elif s == PLAYER_SEND_PAUSE:
                if self.pause(): sRet = 1
            elif s == PLAYER_SEND_GETSTATUS:
                if self.getStatus(): sRet = 1
            elif s == PLAYER_SEND_SPEED:
                if self.setSpeed(): sRet = 1
            elif s == PLAYER_SEND_KEY:
                if self.setKey(): sRet = 1
            elif s == PLAYER_SEND_FREQ:
                if self.setFreq(): sRet = 1
            elif s == PLAYER_SEND_VOLUME:
                if self.setVolume(): sRet = 1
            elif s == PLAYER_SEND_GETPOSITION:
                if self.getPosition(): sRet = 1
            elif s == PLAYER_SEND_SETPOSITION:
                if self.setPosition(): sRet = 1
            elif s == PLAYER_SEND_GETLENGTH:
                if self.getLength(): sRet = 1
            elif s == PLAYER_SEND_STOP:
                if self.stop(): sRet = 1
            # 設定
            elif s == PLAYER_SEND_SETNETTIMEOUT:
                pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_TIMEOUT, _memory[self.__id][M_VALUE])
                pybass.BASS_SetConfig(pybass.BASS_CONFIG_NET_READTIMEOUT, _memory[self.__id][M_VALUE])
                sRet = 1
            elif s == PLAYER_SEND_REPEAT:
                self.__repeat = _memory[self.__id][M_VALUE]
                sRet = 1
            elif s == PLAYER_SEND_SETHLSDELAY:
                if pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY, _memory[self.__id][M_VALUE]): sRet = 1
            elif s == PLAYER_SEND_AUTOCHANGE:
                self.__autoChange = _memory[self.__id][M_VALUE]
                sRet = 1
            else: sRet = 0
            
            if sRet == 1: _memory[self.__id][M_STATUS] = PLAYERSTATUS_STATUS_OK
            elif sRet == -1: _memory[self.__id][M_STATUS] = PLAYERSTATUS_STATUS_FAILD

            # 再生監視
            a = pybass.BASS_ChannelIsActive(self.__handle)
            if a == pybass.BASS_ACTIVE_PAUSED_DEVICE: 
                self.__autoChangeDevice()
            elif a == pybass.BASS_ACTIVE_STALLED or (a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag and self.__sourceType == PLAYER_SOURCETYPE_STREAM):
                if not self.play():
                    self.__eofFlag == True
                    self.stop()
            elif a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag and self.__sourceType == PLAYER_SOURCETYPE_FILE:
                if pybass.BASS_ChannelGetPosition(self.__handle, pybass.BASS_POS_BYTE) == pybass.BASS_ChannelGetLength(self.__handle, pybass.BASS_POS_BYTE) != -1:
                    if self.__repeat: self.play()
                    else:
                        self.__eofFlag = True
                        self.stop()
        return

    def bassInit(self, selfCall=False):
        """ bass.dll初期化() => bool """
        ret = False
        if selfCall: device = PLAYER_DEFAULT_SPEAKER
        else: device = _playerList[self.__id].getConfig(PLAYER_CONFIG_DEVICE)
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
        if ret and self.__playingFlag: self.reStartPlay()
        return ret

    def __del__(self):
        if _playerList[self.__id] == None: return
        pybass.BASS_Free()
        _playerList[self.__id] = None
        _memory[self.__id] = None
    
    
    def __autoChangeDevice(self):
        self.bassFree()
        if self.__autoChange:self.bassInit(True)
        
    def bassFree(self):
        """ 再生位置を保存してデバイスをFree """
        posBTmp = pybass.BASS_ChannelGetPosition(self.__handle, pybass.BASS_POS_BYTE)
        if posBTmp != -1: self.__positionTmp = pybass.BASS_ChannelBytes2Seconds(self.__handle, posBTmp)
        else: self.__positionTmp = -1
        pybass.BASS_Free()
        
    def reStartPlay(self):
        """ 再生復旧 => bool """
        if _playerList[self.__id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_PATH:
            self.createHandle()
        elif _playerList[self.__id].getConfig(PLAYER_CONFIG_SOURCETYPE) == PLAYER_SOURCETYPE_URL:
            self.createHandleFromURL()
        if self.__positionTmp != -1:
            posB = pybass.BASS_ChannelSeconds2Bytes(self.__handle, self.__positionTmp)
            pybass.BASS_ChannelSetPosition(self.__handle, posB, pybass.BASS_POS_BYTE)
        return self.play()

    
    def createHandle(self):
        """ ハンドル作成 => bool """
        self.stop()
        self.__eofFlag = False
        self.__playingFlag = False
        source = _playerList[self.__id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateFile(False,source, 0, 0, pybass.BASS_UNICODE | pybass.BASS_STREAM_PRESCAN | pybass.BASS_STREAM_DECODE)
        reverseHandle = bassFx.BASS_FX_ReverseCreate(handle,0.3,bassFx.BASS_FX_FREESOURCE | pybass.BASS_STREAM_DECODE)
        handle = bassFx.BASS_FX_TempoCreate(handle,0)
        pybass.BASS_ChannelSetAttribute(reverseHandle,bassFx.BASS_ATTRIB_REVERSE_DIR,bassFx.BASS_FX_RVS_FORWARD)
        if handle and reverseHandle:
            # サンプリングレートを読み込み
            cFreq = ctypes.c_float()
            pybass.BASS_ChannelGetAttribute(handle, pybass.BASS_ATTRIB_FREQ, cFreq)
            self.__handle = handle
            self.__reverseHandle = reverseHandle
            self.__freq = round(cFreq.value)
            self.__sourceType = PLAYER_SOURCETYPE_FILE
            return True
        else: return False

    def createHandleFromURL(self):
        """ URLからハンドル作成 => bool """
        self.stop()
        self.__eofFlag = False
        self.__playingFlag = False
        source = _playerList[self.__id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateURL(source.encode(), 0, 0, 0, 0)
        if handle:
            self.__handle = handle
            self.__reverseHandle = 0
            self.__freq = 0
            if self.getLength() == -1: self.__sourceType = PLAYER_SOURCETYPE_STREAM
            else: self.__sourceType = PLAYER_SOURCETYPE_FILE
            self.__handle
            return True
        else: return False

    def play(self):
        """ 再生 """
        ret = pybass.BASS_ChannelPlay(self.__handle, False)
        if ret: self.__playingFlag = True
        else: self.__playingFlag = False
        return ret

    def pause(self):
        """ 一時停止 => bool """
        return pybass.BASS_ChannelPause(self.__handle)

    def stop(self):
        """ 停止 => bool """
        pybass.BASS_StreamFree(self.__handle)
        self.__init__(self.__id, True)
        return True

    def getStatus(self):
        """ ステータス取得 => True"""
        if pybass.BASS_GetDevice() == 4294967295:
            _memory[self.__id][M_VALUE] = PLAYER_STATUS_DEVICEERROR
            return True
        if self.__playingFlag and pybass.BASS_ChannelIsActive(self.__handle) == pybass.BASS_ACTIVE_PLAYING:
            _memory[self.__id][M_VALUE] = PLAYER_STATUS_PLAYING
        elif self.__eofFlag and self.__sourceType == PLAYER_SOURCETYPE_FILE: _memory[self.__id][M_VALUE] = PLAYER_STATUS_EOF
        elif self.__eofFlag and self.__sourceType == PLAYER_SOURCETYPE_STREAM: _memory[self.__id][M_VALUE] = PLAYER_STATUS_STREAMEND
        elif pybass.BASS_ChannelIsActive(self.__handle) == pybass.BASS_ACTIVE_PAUSED: _memory[self.__id][M_VALUE] = PLAYER_STATUS_PAUSED
        elif self.__playingFlag: _memory[self.__id][M_VALUE] = PLAYER_STATUS_LOADING
        else: _memory[self.__id][M_VALUE] = PLAYER_STATUS_STOPPED
        return True


    def setSpeed(self):
        """ 再生速度設定 => bool"""
        speed = _playerList[self.__id].getConfig(PLAYER_CONFIG_SPEED)
        return pybass.BASS_ChannelSetAttribute(self.__handle,bassFx.BASS_ATTRIB_TEMPO, speed)

    def setKey(self):
        """ 再生キー設定 => bool"""
        key = _playerList[self.__id].getConfig(PLAYER_CONFIG_KEY)
        return pybass.BASS_ChannelSetAttribute(self.__handle,bassFx.BASS_ATTRIB_TEMPO_PITCH, key)

    def setFreq(self):
        """ 再生周波数設定 => bool"""
        freqArg = _playerList[self.__id].getConfig(PLAYER_CONFIG_FREQ)
        freq = round((freqArg * self.__freq) / 100)
        return pybass.BASS_ChannelSetAttribute(self.__handle,bassFx.BASS_ATTRIB_TEMPO_FREQ, freq)

    def setVolume(self):
        """ 再生音量設定 => bool"""
        vol = _playerList[self.__id].getConfig(PLAYER_CONFIG_AMPVOL)
        return pybass.BASS_ChannelSetAttribute(self.__handle, pybass.BASS_ATTRIB_VOL, vol)

    def getPosition(self):
        """  再生位置秒数取得 => bool (value)"""
        byte = pybass.BASS_ChannelGetPosition(self.__handle, pybass.BASS_POS_BYTE)
        if byte != -1:
            sec = pybass.BASS_ChannelBytes2Seconds(self.__handle, byte)
            _memory[self.__id][M_VALUE] = sec
            return True
        else: return False

    def setPosition(self):
        """ 秒数で再生位置を設定 => bool """
        sec = _memory[self.__id][M_VALUE]
        byte = pybass.BASS_ChannelSeconds2Bytes(self.__handle, sec)
        if self.__sourceType == PLAYER_SOURCETYPE_FILE: return pybass.BASS_ChannelSetPosition(self.__handle, byte, pybass.BASS_POS_BYTE)
        else: return False

    def getLength(self):
        """  合計時間秒数取得 => bool (value)"""
        byte = pybass.BASS_ChannelGetLength(self.__handle, pybass.BASS_POS_BYTE)
        if byte != -1:
            sec = pybass.BASS_ChannelBytes2Seconds(self.__handle, byte)
            _memory[self.__id][M_VALUE] = sec
        else: _memory[self.__id][M_VALUE] = -1
        return True
