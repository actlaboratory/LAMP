#buttonBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>


import wx

class button(wx.Button):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = True #キーボードフォーカスの初期値
        return super().__init__(*pArg, **kArg)

    def AcceptsFocusFromKeyboard(self):
        return self.focusFromKbd
