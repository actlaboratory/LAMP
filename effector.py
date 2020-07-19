from views import effectorDialog
import wx
import globalVars

def effector():
    d = effectorDialog.Dialog()
    d.Initialize()
    d.Show()
