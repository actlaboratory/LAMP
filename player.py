import sys, platform, globalVars

def is64Bit():
    return sys.maxsize > 2 ** 32

#使用環境に応じて適切なdllをロード
if is64Bit():
    from pybass64 import pybass
    from pybass64 import bass_fx
else:
    from pybass import pybass
    from pybass import bass_fx


class player():
    def __init__ (self):
        # 必要な変数を生成
        self.fileName = None
        self.handle = False
        self.reverseHandle = 0
        self.moveTempo = -100.0
        self.rewindFlag = 0
        self.fastForwardFlag = 0
        self.handleVolume = 1.0
        self.setVolume(globalVars.app.config.getint("volume", "default", default=100)) #音量読み込み
        #bass.dllの初期化
        pybass.BASS_Init(-1, 44100, 0, 0, 0)
        pybass.BASS_SetConfig(pybass.BASS_CONFIG_BUFFER, 150)

    def inputFile(self, fileName):
        # 以前のストリームがあればフリー
        if not(self.handle == 0 and self.reverseHandle == 0):
            self.channelFree()

        # ファイルが渡されたファイルを登録してストリームを生成
        self.fileName = fileName
        self.handle, self.reverseHandle = self.createChannel()

        #早送りとかの設定をリセットして再生
        self.fastMoveReset()
        rtn = self.channelPlay()
        return rtn

    def createChannel(self):
        #ファイルを読み込み、ストリームを生成
        handle = pybass.BASS_StreamCreateFile(False,self.fileName, 0, 0, pybass.BASS_UNICODE | pybass.BASS_STREAM_PRESCAN | pybass.BASS_STREAM_DECODE)

        #逆再生用のストリームを生成。さっきのhandleはこれと同時にfreeする
        reverseHandle = bass_fx.BASS_FX_ReverseCreate(handle,0.3,bass_fx.BASS_FX_FREESOURCE | pybass.BASS_STREAM_DECODE)

        #再生速度をコントロールするストリームを生成。
        handle = bass_fx.BASS_FX_TempoCreate(reverseHandle,0)        #bass_fx.BASS_FX_FREESOURCEしない

        #再生の向きを元の方向に設定
        pybass.BASS_ChannelSetAttribute(reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR,bass_fx.BASS_FX_RVS_FORWARD)

        #再生ボリュームを初期設定
        pybass.BASS_ChannelSetAttribute(handle, pybass.BASS_ATTRIB_VOL, self.handleVolume)

        #2つのhandleを返す
        return handle,reverseHandle

    def channelPlay(self):
        rtn = pybass.BASS_ChannelPlay(self.handle,False)
        # pybass.play_handle(self.handle, show_tags = True)
        return rtn

    def channelFree(self):
        pybass.BASS_StreamFree(self.reverseHandle)
        self.reverseHandle = 0
        pybass.BASS_StreamFree(self.handle)
        self.handle = 0
        self.fastMoveReset()
        self.fileName = None

    def pauseChannel(self):
        return pybass.BASS_ChannelPause(self.handle)


    def getChannelState(self):
        bassCode = pybass.BASS_ChannelIsActive(self.handle)
        if bassCode == pybass.BASS_ACTIVE_PLAYING:
            return 0
        elif bassCode == pybass.BASS_ACTIVE_PAUSED:
            return 1
        else:
            if self.handle == False:
                return 3
            else:
                return 2

    def getChannelLength(self):
        byte = pybass.BASS_ChannelGetLength(self.handle,pybass.BASS_POS_BYTE)
        return pybass.BASS_ChannelBytes2Seconds(self.handle, byte)
    
    def getChannelPosition(self):
        channelPositionByte = pybass.BASS_ChannelGetPosition(self.handle, pybass.BASS_POS_BYTE)
        channelPositionSec = pybass.BASS_ChannelBytes2Seconds(self.handle, channelPositionByte)
        return channelPositionSec

    def setChannelPosition(self, sec):
        channelPositionByte = pybass.BASS_ChannelSeconds2Bytes(self.handle, sec)
        return pybass.BASS_ChannelSetPosition(self.handle, channelPositionByte, pybass.BASS_POS_BYTE)

    def rewind(self):
        if self.fastForwardFlag == 0 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
            pybass.BASS_ChannelSetAttribute(self.reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR,bass_fx.BASS_FX_RVS_REVERSE)
            self.rewindFlag=1
            if self.moveTempo < 500.0:
                self.moveTempo += 50.0
                pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,self.moveTempo)
                pybass.BASS_ChannelSetAttribute(self.reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR,bass_fx.BASS_FX_RVS_REVERSE)
        elif self.fastForwardFlag == 1 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
            self.fastMoveReset()
            
    def fastForward(self):
        if self.rewindFlag == 0 and self.moveTempo < 500.0 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
            self.moveTempo += 50.0
            pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,self.moveTempo)
            self.fastForwardFlag = 1
        elif self.rewindFlag == 1 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
            self.fastMoveReset()

    def fastMoveReset(self):
        self.moveTempo = -100.0    
        self.rewindFlag = 0
        self.fastForwardFlag = 0
        pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,0.0)
        pybass.BASS_ChannelSetAttribute(self.reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR, bass_fx.BASS_FX_RVS_FORWARD)
        pybass.BASS_ChannelUpdate(self.handle, 0)

    # 音量変更（整数%）
    def changeVolume(self, num):
        if num < 0 or num > 200:
            return
        num = num/100
        self.handleVolume = num
        pybass.BASS_ChannelSetAttribute(self.handle, pybass.BASS_ATTRIB_VOL, self.handleVolume)

    def getVolume(self):
        return self.handleVolume*100

    # 音量設定（整数%）
    def setVolume(self, num):
        num = num/100
        self.handleVolume = num
        if self.handleVolume < 0.0:
            self.handleVolume = 0.0
        elif self.handleVolume > 2.0:
            self.handleVolume = 2.0
        pybass.BASS_ChannelSetAttribute(self.handle, pybass.BASS_ATTRIB_VOL, self.handleVolume)

class state():
    PLAYING = 0
    PAUSED = 1
    STOPED = 2
    COLD = 3