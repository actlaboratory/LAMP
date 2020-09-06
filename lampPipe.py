import namedPipe, globalVars, constants, sys


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
    globalVars.eventProcess.forcePlay(msg)
    print(msg)