from views import effectorDialog
import wx
import globalVars

def effector():
    d = effectorDialog.Dialog()
    d.Initialize()
    r = d.Show()
    if r == wx.ID_CANCEL:
        return
    elif r == d.RESET:
        resetEffect()
    else:
        setEffect(d)

def setEffect(d):
    t = d.GetData()
    globalVars.play.setTempo(t[d.TEMPO])
    globalVars.play.setPitch(t[d.PITCH])
    globalVars.play.setFreq(t[d.FREQ])

def resetEffect():
    globalVars.play.setTempo(0)
    globalVars.play.setPitch(0)
    globalVars.play.setFreq(100)
