import sys, ctypes, os, threading, winsound, time
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
        else: newList.append("")
        index += 1
    for i in range(len(_deviceList), len(newList)):
        _deviceList.append(newList[i])
    return _deviceList
getDeviceList()

def bassInit(playerID):
    """BASS初期化要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_INIT
    return _waitReturn(playerID)

def kill(playerID):
    """bassスレッド終了（playerID）"""
    if  _playerList[playerID] != None: _memory[playerID][M_STATUS] = PLAYER_SEND_KILL

def setFile(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_FILE
    return _waitReturn(playerID)

def setURL(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_URL
    return _waitReturn(playerID)

def play(playerID):
    """ 再生(playerID) => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_PLAY
    return _waitReturn(playerID)

def pause(playerID):
    """ 一時停止(playerID) => bool """
    _memory[playerID][M_STATUS] = PLAYER_SEND_PAUSE
    return _waitReturn(playerID)

def getStatus(playerID):
    """ ステータス取得要求(playerID) => ステータス定数 """
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

def getPosition(playerID):
    """ 再生位置取得要求（playerID） => int 秒数 """
    _memory[playerID][M_STATUS] = PLAYER_SEND_GETPOSITION
    if _waitReturn(playerID): return _memory[playerID][M_VALUE]
    else: return 0

def setPosition(playerID, second):
    """ 再生位置設定要求（playerID, int 秒数） => bool """
    _memory[playerID][M_VALUE] = second
    _memory[playerID][M_STATUS] = PLAYER_SEND_SETPOSITION
    return _waitReturn(playerID)

def _waitReturn(playerID):
    """ 処理が終わるまで待機（playerID） => bool """
    print(_memory[playerID][M_STATUS])
    while True:
        time.sleep(0.02)
        if _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_OK:
            print("TRUE")
            return True
        elif _memory[playerID][M_STATUS] == PLAYERSTATUS_STATUS_FAILD:
            print("FALSE")
            return False

class bassThread(threading.Thread):
    def __init__(self, playerID):
        super().__init__()
        # プラグイン適用
        pybass.BASS_PluginLoad(b"basshls.dll", 0)
        pybass.BASS_SetConfig(bassHls.BASS_CONFIG_HLS_DELAY,10)

        # 初期化
        self.__id = playerID
        self.__sourceType = PLAYER_SOURCETYPE_NUL
        self.__playingFlag = False
        self.__eofFlag = False
        self.__handle = 0
        self.__reverseHandle = 0
        self.__freq = 0

    def run(self):
        errorCode = 0
        state = 0
        while True:
            time.sleep(0.02)

            # 通信
            sRet = -1
            s = _memory[self.__id][M_STATUS]
            if s == PLAYER_SEND_INIT:
                if self.bassInit():sRet = 1
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
            elif s == PLAYER_SEND_GETPOSITION:
                if self.getPosition(): sRet = 1
            elif s == PLAYER_SEND_SETPOSITION:
                if self.setPosition(): sRet = 1
            else: sRet = 0
            if sRet == 1: _memory[self.__id][M_STATUS] = PLAYERSTATUS_STATUS_OK
            elif sRet == -1: _memory[self.__id][M_STATUS] = PLAYERSTATUS_STATUS_FAILD

            # 再生継続処理
            a = pybass.BASS_ChannelIsActive(self.__handle)
            if a == pybass.BASS_ACTIVE_STALLED or (a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag and self.__sourceType == PLAYER_SOURCETYPE_URL):
                if not self.play(): self.__playingFlag = False
            elif a == pybass.BASS_ACTIVE_STOPPED and self.__playingFlag and self.__sourceType == PLAYER_SOURCETYPE_FILE:
                self.__eofFlag = True
            
            #DEBUG ----------
            errorTmp = errorCode
            errorCode = pybass.BASS_ErrorGetCode()
            if errorTmp != errorCode:
                print("error: " + str(errorCode))
                winsound.Beep(1300, 500)
            stateTmp = state
            state = pybass.BASS_ChannelIsActive(self.__handle)
            if stateTmp != state:
                if state == pybass.BASS_ACTIVE_STOPPED: print("state: STOP")
                elif state == pybass.BASS_ACTIVE_STALLED: print("state: STALLED")
                elif state == pybass.BASS_ACTIVE_PLAYING: print("state: PLAYING")
                elif state == pybass.BASS_ACTIVE_PAUSED: print("state: PAUSED")
                elif state == pybass.BASS_ACTIVE_PAUSED_DEVICE: print("state: PAUSED_DEVICE")
                winsound.Beep(1500, 500)
        return super().run()

    def bassInit(self):
        """ bass.dll初期化() => bool """
        device = _playerList[self.__id].getConfig(PLAYER_CONFIG_DEVICE)
        if device == PLAYER_DEFAULT_SPEAKER:
            return pybass.BASS_Init(-1, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        elif device == PLAYER_ANY_SPEAKER:
            for i in range(len(getDeviceList()) - 2):
                if pybass.BASS_Init(i + 1, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0):
                    return True
        elif device == PLAYER_NO_SPEAKER:
            return pybass.BASS_Init(0, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        else:
            return pybass.BASS_Init(device, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
        return False

    def __del__(self):
        if _playerList[self.__id] == None: return
        pybass.BASS_Free()
        _playerList[self.__id] = None
        _memory[self.__id] = None
    
    def createHandle(self):
        """ ハンドル作成 => bool """
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
        self.__eofFlag = False
        self.__playingFlag = False
        source = _playerList[self.__id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateURL(source.encode(), 0, 0, 0, 0)
        if handle:
            self.__handle = handle
            self.__reverseHandle = 0
            self.__freq = 0
            self.__sourceType = PLAYER_SOURCETYPE_URL
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

    def getStatus(self):
        """ ステータス取得 => True"""
        if self.__playingFlag and pybass.BASS_ChannelIsActive(self.__handle) == pybass.BASS_ACTIVE_PLAYING:
            _memory[self.__id][M_VALUE] = PLAYER_STATUS_PLAYING
        elif self.__eofFlag: _memory[self.__id][M_VALUE] = PLAYER_STATUS_EOF
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
        return pybass.BASS_ChannelSetPosition(self.__handle, byte, pybass.BASS_POS_BYTE)
