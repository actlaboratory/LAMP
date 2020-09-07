import wx, namedPipe, globalVars, constants, sys, os, m3uManager


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
        if os.path.splitext(msg)[1] == ".mp3":
            wx.CallAfter(globalVars.eventProcess.forcePlay, msg)
        elif os.path.splitext(msg)[1] == ".m3u" or os.path.splitext(msg)[1] == ".m3u8":
            wx.CallAfter(m3uManager.loadM3u, msg, m3uManager.REPLACE)
