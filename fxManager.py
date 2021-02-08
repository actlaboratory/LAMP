# fx manager
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import globalVars
from soundPlayer.fxPlayer import *
from soundPlayer.constants import *
import globalVars

def processing():
    if _notiSound(): playFx("./fx/processing.mp3", _notiDevice())

def confirm():
    if _notiSound(): playFx("./fx/confirm.mp3", _notiDevice())

def load():
    if _notiSound(): playFx("./fx/load.mp3", _notiDevice())

def error():
    if _notiSound(): playFx("./fx/error.mp3", _notiDevice())

def _notiSound():
    return globalVars.app.config.getboolean("notification", "sound", True)

def _notiDevice():
    dl = getDeviceList()
    dl[0] = "default"
    dl.append("same")
    dc = globalVars.app.config.getstring("notification", "outputDevice", "default", dl)
    if dc == "default": return PLAYER_DEFAULT_SPEAKER
    elif dc == "same":
        md = globalVars.play.getConfig(PLAYER_CONFIG_DEVICE)
        if md > 0 and md < len(dl) - 1: return dl[md]
        else: return PLAYER_DEFAULT_SPEAKER
    else: return dc
