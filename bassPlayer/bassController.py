import sys, ctypes, os, threading
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
_handles = []
H_STATOUS = 0
H_HANDLE = 1
H_REVERSE = 2 #ファイルの場合のみ
H_FREQ = 3 #ファイルのみ



def connectPlayer(playerObject):
    """
    プレイヤーと接続(playerオブジェクト) => int PlayerID
    プレイヤーオブジェクトに対して固有のIDを発行し、設定情報を連携する、
    """
    _playerList.append(playerObject)
    index = len(_playerList) - 1
    _handles.append([PLAYER_STATOUS_OK, 0])
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
    _handles[playerID][H_STATOUS] = PLAYER_SEND_INIT
    return _waitReturn(playerID)

def setFile(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _handles[playerID][H_STATOUS] = PLAYER_SEND_FILE
    return _waitReturn(playerID)

def setURL(playerID):
    """ ファイルストリームの生成要求（playerID） => bool """
    _handles[playerID][H_STATOUS] = PLAYER_SEND_URL
    return _waitReturn

def play(playerID):
    """ 再生(playerID) => bool """
    _handles[playerID][H_STATOUS] = PLAYER_SEND_PLAY
    return _waitReturn(playerID)

def pause(playerID):
    """ 一時停止(playerID) => bool """
    _handles[playerID][H_STATOUS] = PLAYER_SEND_PAUSE
    return _waitReturn(playerID)

def _waitReturn(playerID):
    """ 処理が終わるまで待機（playerID） => bool """
    while True:
        if _handles[playerID][H_STATOUS] == PLAYER_STATOUS_OK: return True
        elif _handles[playerID][H_STATOUS] == PLAYER_STATOUS_FAILD: return False

class bassThread(threading.Thread):
    def __init__(self, playerID):
        super().__init__()
        self.id = playerID
        self.sourceType = None

    def run(self):
        errorCode = 0
        while True:
            # 通信
            s = _handles[self.id][H_STATOUS]
            if s == PLAYER_SEND_INIT:
                if self.bassInit(): _handles[self.id][H_STATOUS] = PLAYER_STATOUS_OK
                else: _handles[self.id][H_STATOUS] = PLAYER_STATOUS_FAILD
            elif s == PLAYER_SEND_FILE:
                if self.createHandle(): _handles[self.id][H_STATOUS] = PLAYER_STATOUS_OK
                else: _handles[self.id][H_STATOUS] = PLAYER_STATOUS_FAILD
            elif s == PLAYER_SEND_URL:
                if self.createHandleFromURL(): _handles[self.id][H_STATOUS] = PLAYER_STATOUS_OK
                else: _handles[self.id][H_STATOUS] = PLAYER_STATOUS_FAILD
            elif s == PLAYER_SEND_PLAY:
                if self.play(): _handles[self.id][H_STATOUS] = PLAYER_STATOUS_OK
                else: _handles[self.id][H_STATOUS] = PLAYER_STATOUS_FAILD
            elif s == PLAYER_SEND_PAUSE:
                if self.pause(): _handles[self.id][H_STATOUS] = PLAYER_STATOUS_OK
                else: _handles[self.id][H_STATOUS] = PLAYER_STATOUS_FAILD
            errorTmp = errorCode
            errorCode = pybass.BASS_ErrorGetCode()
            if errorTmp != errorCode: print(errorCode)
        return super().run()

    def bassInit(self):
        """ bass.dll初期化() => bool """
        device = _playerList[self.id].getConfig(PLAYER_CONFIG_DEVICE)
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


    def createHandle(self):
        """ ハンドル作成 => bool """
        source = _playerList[self.id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateFile(False,source, 0, 0, pybass.BASS_UNICODE | pybass.BASS_STREAM_PRESCAN | pybass.BASS_STREAM_DECODE)
        reverseHandle = bassFx.BASS_FX_ReverseCreate(handle,0.3,bassFx.BASS_FX_FREESOURCE | pybass.BASS_STREAM_DECODE)
        handle = bassFx.BASS_FX_TempoCreate(handle,0)
        pybass.BASS_ChannelSetAttribute(reverseHandle,bassFx.BASS_ATTRIB_REVERSE_DIR,bassFx.BASS_FX_RVS_FORWARD)
        if handle and reverseHandle:
            # サンプリングレートを読み込み
            cFreq = ctypes.c_float()
            pybass.BASS_ChannelGetAttribute(handle, pybass.BASS_ATTRIB_FREQ, cFreq)
            _handles[self.id] = [PLAYER_STATOUS_OK, handle, reverseHandle, round(cFreq.value)]
            return True
        else: return False

    def createHandleFromURL(self):
        """ URLからハンドル作成 => bool """
        source = _playerList[self.id].getConfig(PLAYER_CONFIG_SOURCE)
        handle = pybass.BASS_StreamCreateURL(source.encode(), 0, 0, 0, 0)
        if handle:
            _handles[self.id] = [PLAYER_STATOUS_OK, handle, ]
            return True
        else: return False

    def play(self):
        """ 再生 """
        return pybass.BASS_ChannelPlay(_handles[self.id][H_HANDLE], False)

    def pause(self):
        """ 一時停止 => bool """
        return pybass.BASS_ChannelPause(_handles[self.id][H_HANDLE])
