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
        self.setEffect(d.GetData())

def setEffect(val):
    globalVars.play.setTempo(val)