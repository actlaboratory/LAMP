# -*- coding: utf-8 -*-
#Simple dialog

import ctypes
import wx

def winDialog(title,message):
	ctypes.windll.user32.MessageBoxW(0,message,title,0x00000040)

def dialog(title,message):
	ctypes.windll.user32.MessageBoxW(0,message,title,0x00000040)

def errorDialog(message):
	dialog = wx.MessageDialog(None,message,"error",wx.OK|wx.ICON_ERROR)
	dialog.ShowModal()
	dialog.Destroy()
	return
