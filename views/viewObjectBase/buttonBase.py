#buttonBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>


import wx
from views.viewObjectBase import viewObjectUtil, toolTipBase

class button(wx.Button):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = viewObjectUtil.popArg(kArg, "enableTabFocus", True)     #キーボードフォーカスの初期値
        super().__init__(*pArg, **kArg)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        # ツールチップ設定
        self.toolTip = None
        self.toolTipLabel = None
        self.enableToolTip = False

    def AcceptsFocusFromKeyboard(self):
        return self.focusFromKbd
    
    def setToolTip(self, label=None):
        """
        ツールチップをセット、またはチップラベルを変更します。

        :param str/None label: ラベル。デフォルトはボタンラベルと同期
        """
        self.toolTipLabel = label
        if self.enableToolTip == False:
            self.enableToolTip = True
        elif self.enableToolTip and self.toolTip != None:
            if self.toolTipLabel == None: self.toolTip.refresh(label=self.Label)
            else: self.toolTip.refresh(label=self.toolTipLabel)
    
    def onMouseEnter(self, evt):
        if self.toolTip == None and self.enableToolTip:
            if self.toolTipLabel == None:
                self.toolTip = toolTipBase.toolTip(self, self.ClientToScreen(evt.GetPosition()), self.Label, self.GetBackgroundColour(), self.GetForegroundColour(), self.GetFont())
            else:
                self.toolTip = toolTipBase.toolTip(self, self.ClientToScreen(evt.GetPosition()), self.toolTipLabel, self.GetBackgroundColour(), self.GetForegroundColour(), self.GetFont())
    
    def onMouseLeave(self, evt):
        if self.toolTip != None:
            self.toolTip.destroy()
            self.toolTip = None
