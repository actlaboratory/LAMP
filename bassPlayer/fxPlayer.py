import time, threading, os
from . import bassController
from .constants import *

class _fxPlayerObject():
    def __init__(self, source, repeat=True, device=PLAYER_DEFAULT_SPEAKER, volume=100, system=False):
        """ init（音源, リピート=True, 再生デバイス=デフォルト, 音量=100） """
        self.__device = device
        self.__source = source
        self.__volume = volume
        self.__id = bassController.connectPlayer(self)
        self.__isDeleted = False
        self.setDevice(device)
        bassController.setRepeat(self.__id, repeat)
        bassController.setAutoChangeDevice(self.__id, False)
        bassController.setFile(self.__id)
        result = self.play()
        if system and not repeat and result:
            auto = threading.Thread(target=self.__autoStopper)
            auto.start()

    def getConfig(self, config):
        """ 設定読み出し(設定読み出し定数) =>　mixed """
        if config == PLAYER_CONFIG_DEVICE: return self.__device
        if config == PLAYER_CONFIG_ID: return self.__id
        if config == PLAYER_CONFIG_SOURCE: return self.__source
        if config == PLAYER_CONFIG_SOURCETYPE: return PLAYER_SOURCETYPE_PATH
        if config == PLAYER_CONFIG_SPEED: return 100
        if config == PLAYER_CONFIG_KEY: return 0
        if config == PLAYER_CONFIG_FREQ: return 100
        if config == PLAYER_CONFIG_AMPVOL: return self.__volume
        if config == PLAYER_CONFIG_VOLUME: return self.__volume

    def setDevice(self, device, change=True):
        """ インデックス、または定数から再生デバイスをセット(int インデックス, 変更扱い=True) => None """
        if device < len(bassController.getDeviceList()) and device > 0: self.__device = device
        elif device == PLAYER_NO_SPEAKER: self.__device = PLAYER_NO_SPEAKER
        elif device == PLAYER_DEFAULT_SPEAKER and len(bassController.getDeviceList()) > 1: self.__device = PLAYER_DEFAULT_SPEAKER
        else: return False
        bassController.changeDevice(self.__id)
    
    def __autoStopper(self):
        """ 単発再生用自動停止 （スレッド呼び出し必須）"""
        counter = 0
        while bassController.getStatus(self.__id) == PLAYER_STATUS_PLAYING:
            time.sleep(0.1)
            counter += 1
            if counter > 600: break
        self.__del__()

    def isPlaying(self):
        """ 再生中? => bool """
        if bassController.getStatus(self.__id) == PLAYER_STATUS_PLAYING: return True
        else: return False
    
    def play(self):
        """ 再生 => bool """
        return bassController.play(self.__id)
    
    def stop(self):
        """ 停止 """
        self.__del__()

    def __del__(self):
        if not self.__isDeleted:
            self.__isDeleted = True
            bassController.exitPlayer(self.__id)

def playFx(source, device=PLAYER_DEFAULT_SPEAKER, volume=100):
    """
    効果音再生（音源, 再生デバイス=デフォルト, 音量=100） => bool
    60秒以内の効果音ファイルを１度再生する。
    """
    p = _fxPlayerObject(source, False, device, volume, True)
    ret = p.play()
    if ret: return True
    else:
        p.__del__()
        return False

def fxObject(source, repeat=True, device=PLAYER_DEFAULT_SPEAKER, volume=100, system=False):
    """ 効果音オブジェクト（音源, リピート=True, 再生デバイス=デフォルト, 音量=100） => fxPlayerObject """
    return _fxPlayerObject(source, repeat, device, volume, False)

def getDeviceList():
    """ 再生デバイス一覧取得 => リスト """
    return bassController.getDeviceList()
