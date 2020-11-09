import globalVars

skipInterval = (5,30,60,300,600)

#スキップ感覚（秒）
def setSkipInterval(sec):
    if sec in skipInterval:
        globalVars.app.config["player"]["skipInterval"] = str(int(sec))

def getSkipInterval():
    sec = globalVars.app.config.getint("player", "skipInterval", default=30)
    if sec in skipInterval == False:
        sec = 30
    globalVars.app.config["player"]["skipInterval"] = sec
    if sec < 60:
        string = str(int(sec))+_("秒")
    else:
        string = str(int(sec/60))+_("分")
    return (sec,string)
