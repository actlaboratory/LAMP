"""
notificationText
親ウィンドウの中央に通知を表示

Copyright (C) 2020 Hiroki Fujii
"""


import wx
import globalVars
from views.fontManager import FontManager

class _notiDialog(wx.Dialog):
    def AcceptsFocus(self):
        return False

class notification():
    def __init__(self, parent):
        """
        親ウィンドウの中央に通知文字列を表示
        parent:親ウィンドウ        self.panel = wx.Panel()
        """

        self.dialog = _notiDialog()
        self.dialog.Create(parent, style=0)
        self.dialog.SetTransparent(180)
        bgColour = wx.Colour(0, 0, 255)
        self.dialog.SetBackgroundColour(bgColour)
        fgColour = wx.Colour(255, 255, 255)
        self.dialog.SetForegroundColour(fgColour)
        self.dialog.SetFont(FontManager().GetFont())
        self.label = wx.StaticText(self.dialog, label="")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 0, wx.ALIGN_CENTER|wx.ALL, border=20)
        self.dialog.SetSizer(sizer)
        self.dialog.Fit()
        self.dialog.CentreOnParent(wx.BOTH)
        self.dialog.Enable(False)
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.hide)

    def show(self, label, time):
        self.label.SetLabel(label)
        self.timer.Stop()
        self.dialog.Fit()
        self.dialog.CentreOnParent(wx.BOTH)
        self.timer.Start(time * 1000, wx.TIMER_ONE_SHOT)
        self.dialog.Show()

    def hide(self, evt=None):
        self.dialog.Hide()

    def destroy(self):
        self.timer.Destroy()
