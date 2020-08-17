import re, os
from .constants import *
from . import bassController

class player():
    def __init__(self):
        self.__id = bassController.connectPlayer(self)
        self.__device = PLAYER_NO_SPEAKER
        self.__source = None
        self.__speed = 0

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
