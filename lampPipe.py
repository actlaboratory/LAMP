import wx, namedPipe, globalVars, constants, sys, os, m3uManager, listManager


def sendPipe():
    pipeClient = namedPipe.Client(constants.PIPE_NAME)
    while True:
        try:
            pipeClient.connect()
            pipeClient.write(sys.argv[1])
            return
        except namedPipe.PipeServerNotFoundError as e:
            pass
def startPipeServer():
    pipeServer = namedPipe.Server(constants.PIPE_NAME)
    pipeServer.setReceiveCallback(onReceive)
    pipeServer.start()

def onReceive(msg):
    if os.path.isfile(msg):
        if os.path.splitext(msg)[1].lower() in globalVars.fileExpansions:
            setting = globalVars.app.config.getstring("player", "fileInterrupt", "play", ("play", "addPlaylist", "addQueue", "addQueueHead"))
            if setting == "play": wx.CallAfter(globalVars.eventProcess.forcePlay, msg)
            elif setting == "addPlaylist": wx.CallAfter(listManager.addItems, [msg], globalVars.app.hMainView.playlistView)
            elif setting == "addQueue": wx.CallAfter(listManager.addItems, [msg], globalVars.app.hMainView.queueView)
            elif setting == "addQueueHead": wx.CallAfter(listManager.addItems, [msg], globalVars.app.hMainView.queueView, 0)
        elif os.path.splitext(msg)[1].lower() == ".m3u" or os.path.splitext(msg)[1].lower() == ".m3u8":
            setting = globalVars.app.config.getstring("player", "playlistInterrupt", "open", ("open", "add"))
            if setting == "open": wx.CallAfter(m3uManager.loadM3u, msg, m3uManager.REPLACE)
            elif setting == "add": wx.CallAfter(m3uManager.loadM3u, msg, m3uManager.ADD)
