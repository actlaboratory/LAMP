import re, os, threading, time, winsound
from .constants import *
from . import bassController

class player():
    def __init__(self, device=PLAYER_DEFAULT_SPEAKER):
        # init（初期再生デバイス=デフォルト）
        self.__device = PLAYER_NO_SPEAKER
        self.__source = None
        self.__speed = 100
        self.__key = 0
        self.__freq = 100
        self.__amp = 100
        self.__volume = 100
        self.__fastMoveFlag = False
        self.__overRewind = False
        self.__rsvOverRewind = False
        self.__fastMoveThread = threading.Thread()
        self.__id = bassController.connectPlayer(self)
        self.__isDeleted = False
        self.setDevice(device)

    def getConfig(self, config):
        """ 設定読み出し(設定読み出し定数) =>　mixed """
        if config == PLAYER_CONFIG_DEVICE: return self.__device
        if config == PLAYER_CONFIG_ID: return self.__id
        if config == PLAYER_CONFIG_SOURCE: return self.__source
        if config == PLAYER_CONFIG_SOURCETYPE:
            if os.path.isfile(self.__source): return PLAYER_SOURCETYPE_PATH
            if re.search("https?://.+\..+", self.__source) != None: return PLAYER_SOURCETYPE_URL
            self.__source = None
            return PLAYER_SOURCETYPE_NUL
        if config == PLAYER_CONFIG_SPEED: return self.__speed
        if config == PLAYER_CONFIG_KEY: return self.__key
        if config == PLAYER_CONFIG_FREQ: return self.__freq
        if config == PLAYER_CONFIG_AMPVOL: return self.__volume * self.__amp / 100
        if config == PLAYER_CONFIG_VOLUME: return self.__volume
        if config == PLAYER_CONFIG_AMP: return self.__amp

    def setDevice(self, device, change=True):
        """ インデックス、または定数から再生デバイスをセット(int インデックス, 変更扱い=True) => None """
        if device < len(bassController.getDeviceList()) and device > 0: self.__device = device
        elif device == PLAYER_NO_SPEAKER: self.__device = PLAYER_NO_SPEAKER
        elif device == PLAYER_DEFAULT_SPEAKER and len(bassController.getDeviceList()) > 1: self.__device = PLAYER_DEFAULT_SPEAKER
        else: return False
        bassController.changeDevice(self.__id)

        return True

    def getDeviceList(self):
        """ デバイス一覧取得 => list """
        return bassController.getDeviceList()
    
    def setDeviceByName(self, deviceName):
        """ デバイス名から再生デバイスをセット(str デバイス名) => bool """
        try:
            d = bassController.getDeviceList().index(deviceName)
            self.setDevice(d)
            return True
        except ValueError as e:
            return False

    def setNetTimeout(self, miliSec):
        """ ネットワークタイムアウトを設定（int ミリ秒） => bool """
        return bassController.setNetTimeout(self.__id, miliSec)

    def setHlsTimeout(self, sec):
        """ HLS遅延を設定（int 秒） => bool """
        return bassController.setHlsDelay(self.__id, sec)

    def setSource(self, source):
        """ 音源読み込み（str 音源） => bool """
        sourceTmp = self.__source
        self.__source = source
        if self.__sendSource(): return True
        else:
            self.__source = sourceTmp
            return False
    
    def setRepeat(self, boolVal):
        """ リピート（bool）"""
        bassController.setRepeat(self.__id, boolVal)
    
    def __sendSource(self):
        """bassにファイルを送信 => bool"""
        if os.path.isfile(self.__source): return bassController.setFile(self.__id)
        elif re.search("^https?://.+\..+", self.__source) != None: return bassController.setURL(self.__id)
        else: return False

    def play(self):
        """再生 => bool"""
        return bassController.play(self.__id)

    def pause(self):
        """一時停止 => bool"""
        return bassController.pause(self.__id)

    def stop(self):
        """停止 => bool"""
        return bassController.stop(self.__id)

    def getStatus(self):
        """ ステータス取得 => int ステータス定数 => True"""
        if self.__overRewind: return PLAYER_STATUS_OVERREWIND
        return bassController.getStatus(self.__id)
    
    def setSpeed(self, speed):
        """速度設定（int 5..100..5100） => bool"""
        if speed < 5 or speed > 5100: return False
        self.__speed = speed
        return bassController.setSpeed(self.__id)

    def setSpeedByDiff(self, speed):
        """ 差分指定で速度を設定（int +-速度） => bool """
        return self.setSpeed(self.__speed + speed)

    def setKey(self, key):
        """再生キー(高さ)設定（int -60..0..60） => bool"""
        if key < -60 or key > 60: return False
        self.__key = key
        return bassController.setKey(self.__id)

    def setKeyByDiff(self, key):
        """ 差分指定で再生キーを設定（int +-速度） => bool """
        return self.setKey(self.__key + key)

    def setFreq(self, freq):
        """周波数設定（int 6..100..5000） => bool"""
        if freq < 6 or freq > 5000: return False
        self.__freq = freq
        return bassController.setFreq(self.__id)

    def setFreqByDiff(self, freq):
        """ 差分指定で周波数を設定（int +-速度） => bool """
        return self.setFreq(self.__freq + freq)
    
    def setAmp(self, amp):
        """増幅設定（float 0..100..400） => bool"""
        if amp <= 400 and amp >= 0:
            self.__amp = amp
            bassController.setVolume(self.__id)
            return True
        else:
            return False

    def setVolume(self, vol):
        """音量設定（int 0..100） => bool"""
        if vol <= 100 and vol >= 0:
            self.__volume = vol
            bassController.setVolume(self.__id)
            return True
        else:
            return False

    def setVolumeByDiff(self, vol):
        """ 音量増減値設定（int +-差分） => bool """
        val = self.__volume + vol
        if val > 100: return self.setVolume(100)
        elif val < 0: return self.setVolume(0)
        else: return self.setVolume(val)

    def getPosition(self):
        """ 再生位置取得 => int 秒数 or -1"""
        return bassController.getPosition(self.__id)

    def setPosition(self, second):
        """ 再生位置設定（int 秒数） => bool """
        return bassController.setPosition(self.__id, second)

    def getLength(self):
        """
        合計時間取得 => int 秒数
        失敗した場合は -1
        """
        return bassController.getLength(self.__id)

    def fastForward(self):
        """ 早送り 0.1秒未満連続呼び出し中有効 """
        self.__fastMove(1)

    def rewind(self):
        """ 巻き戻し 0.1秒未満連続呼び出しで有効 """
        self.__fastMove(-1)

    def __fastMove(self, direction):
        """
        高速移動（int 方向）
        1 = 早送り, -1 = 巻き戻し
        """
        # フラグ = -2 巻き戻し - 待機処理 - 終了 - 待機処理 - 早送り +2
        if (self.getStatus() != PLAYER_STATUS_PLAYING and self.getStatus() != PLAYER_STATUS_OVERREWIND) or self.getLength() == False: return
        if self.__fastMoveFlag == 0 and not self.__fastMoveThread.isAlive():
            self.__fastMoveThread = threading.Thread(target=self.__fastMover, args=(direction,))
            self.__fastMoveThread.start()
        elif self.__fastMoveFlag == direction: self.__fastMoveFlag = direction * 2

    def overRewindOk(self):
        """ 巻き戻し失敗フラグの受領を通知 """
        self.__overRewind = False

    def stopOverRewind(self):
        """ 巻き戻しができないときに再試行を抑制 """
        self.__rsvOverRewind = True
    
    def __fastMover(self, direction):
        """ スレッド呼び出し用高速移動（int 方向） """
        self.__fastMoveFlag = direction * 2
        counter = 1
        gap = 0.4
        while True:
            #フラグ処理
            if self.__fastMoveFlag != direction * 2: break
            self.__fastMoveFlag = direction
            if self.__rsvOverRewind and direction == -1: #巻き戻しが実行できないらしい
                self.__overRewind = False
                time.sleep(gap)
                continue
            #現在位置取得と加速
            new = self.getPosition()
            if counter < 10: pos = new + direction * gap * 2
            elif counter < 20: pos = new + direction * gap * 4
            elif counter < 30: pos = new + direction * gap * 7
            elif counter < 40: pos = new + direction * gap * 11
            elif counter < 50: pos = new + direction * gap * 16
            elif counter < 60: pos = new + direction * gap * 22
            elif counter < 70: pos = new + direction * gap * 29
            else: pos = new + direction * gap * 37
            #ポジション適用
            if direction == -1 and counter > 1: pos -= gap
            if new != -1:
                if not self.setPosition(pos) and direction == -1:
                    self.setPosition(0)
                    self.__overRewind = True
                elif not self.setPosition(pos) and direction == 1:
                    self.setPosition(self.getLength())
                else: self.__overRewind = False
            else: break
            if counter < 4000: counter += 1
            time.sleep(gap)
        self.__overRewind = False
        self.__rsvOverRewind = False
        self.__fastMoveFlag = False
        return

    def exit(self):
        """ プレイヤー破棄"""
        self.__del__()

    def __del__(self):
        if not self.__isDeleted:
            self.__isDeleted = True
            bassController.exitPlayer(self.__id)
