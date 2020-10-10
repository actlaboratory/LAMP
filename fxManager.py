from soundPlayer.fxPlayer import *
import globalVars

def load():
    if _notiSound(): playFx("./fx/load.mp3")

def error():
    playFx("./fx/error.mp3")

def _notiSound():
    return globalVars.app.config.getboolean("notification", "sound", True)
