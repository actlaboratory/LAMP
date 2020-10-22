from soundPlayer.fxPlayer import *
from soundPlayer.constants import *
import globalVars

def load():
    if _notiSound(): playFx("./fx/load.mp3", _notiDevice())

def error():
    if _notiSound(): playFx("./fx/error.mp3", _notiDevice())

def _notiSound():
    return globalVars.app.config.getboolean("notification", "sound", True)

def _notiDevice():
    dl = getDeviceList()
    dl[0] = "default"
    dc = globalVars.app.config.getstring("notification", "outputDevice", "default", dl)
    if dc == "default": return PLAYER_DEFAULT_SPEAKER
    else: return dc
