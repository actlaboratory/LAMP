from views import effectorDialog
import wx
import globalVars

def effector():
    d = effectorDialog.Dialog()
    d.Initialize()
    r = d.Show()
    if r == wx.ID_CANCEL:
        return
    else:
        setEffect(d)

def setEffect(d):
    t = d.GetData()
    globalVars.play.setTempo(t[d.TEMPO])
    globalVars.play.setPitch(t[d.PITCH])
    globalVars.play.setFreq(t[d.FREQ])
