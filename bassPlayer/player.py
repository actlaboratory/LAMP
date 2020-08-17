import re, os
from .constants import *
from . import bassController

class player():
    def __init__(self):
        self.__id = bassController.connectPlayer(self)
        self.__device = PLAYER_NO_SPEAKER
        self.__source = None
        self.__speed = 0
        self.__key = 0
        self.__freq = 100

    def startDevice(self, device):
        """ デバイススタート(int デバイス) """
        if not self.setDevice(device): self.__device = PLAYER_NO_SPEAKER
        bassController.bassInit(self.__id)
        print(self.__device)
    
    def getConfig(self, config):
        """ 設定読み出し(設定読み出し定数) """
        if config == PLAYER_CONFIG_DEVICE: return self.__device
        if config == PLAYER_CONFIG_ID: return self.__bassAccountID
        if config == PLAYER_CONFIG_SOURCE: return self.__source
        if config == PLAYER_CONFIG_SOURCETYPE:
            if os.path.isfile(self.__source): return PLAYER_SOURCETYPE_FILE
            if re.search("https?://.+\..+", self.__source) != None: return PLAYER_SOURCETYPE_URL
            self.__source = None
            return PLAYER_SOURCETYPE_NUL
        if config == PLAYER_CONFIG_SPEED: return self.__speed
        if config == PLAYER_CONFIG_KEY: return self.__key
        if config == PLAYER_CONFIG_FREQ: return self.__freq
    def setDevice(self, device):
        """ インデックス、または定数から再生デバイスをセット(int インデックス) => None """
        if device < len(bassController.getDeviceList()) and device > 0: self.__device = device
        elif device == PLAYER_NO_SPEAKER: self.__device = PLAYER_NO_SPEAKER
        elif device == PLAYER_DEFAULT_SPEAKER and len(bassController.getDeviceList()) > 1: self.__device = PLAYER_DEFAULT_SPEAKER
        else: return False
        return True

    def setDeviceByName(self, deviceName):
        """ デバイス名から再生デバイスをセット(str デバイス名) => bool """
        try:
            self.__device = bassController.getDeviceList().index(deviceName)
            return True
        except ValueError as e:
            return False

    def setSource(self, source):
        """ 音源読み込み（str 音源） => bool """
        sourceTmp = self.__source
        self.__source = source
        if self.sendSource(): return True
        else:
            self.__source = sourceTmp
            return False
    
    def sendSource(self):
        """bassにファイルを送信 => bool"""

        if os.path.isfile(self.__source): return bassController.setFile(self.__id)
        elif re.search("https?://.+\..+", self.__source) != None: return bassController.setURL(self.__id)

    def play(self):
        """再生 => bool"""
        return bassController.play(self.__id)

    def pause(self):
        """再生 => bool"""
        return bassController.pause(self.__id)

    def setSpeed(self, speed):
        """速度設定（int -95..0..5000） => bool"""
        speedTmp = self.__speed
        self.__speed = speed
        if bassController.setSpeed(self.__id): return True
        else:
            self.__speed = speedTmp
            return False

    def changeSpeed(self, speed):
        """ 差分指定で速度を設定（int +-速度） => bool """
        return self.setSpeed(self.__speed + speed)

    def setKey(self, key):
        """再生キー(高さ)設定（int -60..0..60） => bool"""
        keyTmp = self.__key
        self.__key = key
        if bassController.setKey(self.__id): return True
        else:
            self.__key = keyTmp
            return False

    def changeKey(self, key):
        """ 差分指定で再生キーを設定（int +-速度） => bool """
        return self.setKey(self.__key + key)

    def setFreq(self, freq):
        """周波数設定（int 5..100..5000） => bool"""
        freqTmp = self.__freq
        self.__freq = freq
        if bassController.setFreq(self.__id): return True
        else:
            self.__freq = freqTmp
            return False

    def changeFreq(self, freq):
        """ 差分指定で周波数を設定（int +-速度） => bool """
        return self.setFreq(self.__freq + freq)
    
    def getPosition(self):
        """ 再生位置取得 => int 秒数 """
        return bassController.getPosition(self.__id)

    def setPosition(self, second):
        """ 再生位置設定（int 秒数） => bool """
        return bassController.setPosition(self.__id, second)
