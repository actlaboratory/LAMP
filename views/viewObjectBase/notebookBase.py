#notebookBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>


import wx

class notebook(wx.Notebook):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = True #キーボードフォーカスの初期値
        return super().__init__(*pArg, **kArg)

    def AcceptsFocusFromKeyboard(self):
        return self.focusFromKbd

    def enableFocusFromKeyboard(self, boolVal):
        if boolVal: self.focusFromKbd = True
        else: self.focusFromKbd = False