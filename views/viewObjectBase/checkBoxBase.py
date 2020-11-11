import wx

class checkBox(wx.CheckBox):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = True #キーボードフォーカスの初期値
        super().__init__(*pArg, **kArg)

    def AcceptsFocusFromKeyboard(self):
        return self.focusFromKbd

    def enableFocusFromKeyboard(self, boolVal):
        if boolVal: self.focusFromKbd = True
        else: self.focusFromKbd = False