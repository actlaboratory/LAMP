import wx

class toolTip():
    def __init__(self, parent, cursorPos, label, bgColor, fgColor, font):
        cursorPos.x += 10
        cursorPos.y += 10
        self.dialog = wx.Dialog(parent.GetTopLevelParent(), style=wx.BORDER_RAISED, pos=cursorPos)
        self.dialog.SetBackgroundColour(bgColor)
        self.dialog.SetForegroundColour(fgColor)
        self.dialog.SetFont(font)
        self.staticText = wx.StaticText(self.dialog, wx.ID_ANY, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.staticText, 0, wx.ALIGN_CENTER|wx.ALL, border=2)
        self.dialog.SetSizer(sizer)
        self.dialog.Fit()
        self.dialog.Disable()
        self.dialog.Show()

    def refresh(self, cursorPos=None, label=None):
        if cursorPos != None: self.dialog.Move(cursorPos)
        if label != None: self.staticText.SetLabel(label)
        self.dialog.Fit()

    def destroy(self):
        self.dialog.Destroy()
        self.dialog = None

    def __del__(self):
        if self.dialog != None: self.destroy()
