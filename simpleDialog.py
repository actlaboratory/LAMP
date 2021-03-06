# -*- coding: utf-8 -*-
#Simple dialog

import ctypes
import wx

def winDialog(title,message):
	ctypes.windll.user32.MessageBoxW(0,message,title,0x00000040)

def dialog(title,message,parent=None):
	if parent:
		hwnd = parent.GetHandle()
	else:
		hwnd = 0
	ctypes.windll.user32.MessageBoxW(hwnd,message,title,0x00000040)

def errorDialog(message,parent=None):
	dialog = wx.MessageDialog(parent,message,"error",wx.OK|wx.ICON_ERROR)
	dialog.ShowModal()
	dialog.Destroy()
	return
