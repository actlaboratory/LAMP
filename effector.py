from views import effectorDialog
import wx
import globalVars

def effector():
    d = effectorDialog.Dialog("effectorDialog")
    d.Initialize()
    d.Show()
