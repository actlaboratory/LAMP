# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

from views import effectorDialog
import wx
import globalVars

def effector():
    d = effectorDialog.Dialog("effectorDialog")
    d.Initialize()
    d.Show()
