# -*- coding: utf-8 -*-
# hotkey mapping  manager
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import wx

import keymapHandlerBase
import menuItemsStore

class HotkeyHandler(keymapHandlerBase.KeymapHandlerBase):
	"""
		ホットキーのマッピングを管理する
	"""

	def __init__(self, dict=None, filter=None):
		super().__init__(dict, filter, permitConfrict=permitConfrict)
		self.makeEntry=makeEntry		#エントリ作成関数。Windowsキー利用の為変更

	def Set(self,identifier,window,eventHandler):
		"""
			指定されたウィンドウにホットキーとして登録する
			identifier で、どのビューでのテーブルを取得するかを指定する。
			windowには、登録先としてwx.windowを継承したインスタンスを指定する
			eventHandlerを指定すると、EVT_HOTKEY(id,fnc)をBindする
		"""
		if eventHandler:
			window.Bind(wx.EVT_HOTKEY,eventHandler)
		for entry in self.entries[identifier.upper()]:
			if not window.RegisterHotKey(entry.GetCommand(),entry.GetFlags(),entry.GetKeyCode()):
				self.log.warning("hotkey set failed. ref=%s may be confrict." % entry.GetRefName)
				self.addError(identifier,entry.GetRefName(),"N/A","register failed. may be confrict.")

def makeEntry(ref,key,filter,log):
	"""
		ref(String)と、/区切りでない単一のkey(String)からwx.AcceleratorEntryを生成
		ホットキー専用なのでWindowsキーも修飾キーとして使用可能
	"""
	key=key.upper()					#大文字に統一して処理

	if menuItemsStore.getRef(ref.upper())>49151:		#OSの仕様により0xBFFF=49151までしか利用できない
		log.warning("%s=%d is invalid hotkey ref. hotkey ref must be smaller than 49151" % (ref,menuItemsStore.getRef(ref)))
		return False

	#修飾キーの確認
	ctrl="CTRL+" in key
	alt="ALT+" in key
	shift="SHIFT+" in key
	win="WINDOWS+" in key
	codestr=key.split("+")
	flags=0
	flagCount=0
	if ctrl:
		flags=wx.MOD_CONTROL
		flagCount+=1
	if alt:
		flags=flags|wx.MOD_ALT
		flagCount+=1
	if shift:
		flags=flags|wx.MOD_SHIFT
		flagCount+=1
	if win:
		flags=flags|wx.MOD_WIN
		flagCount+=1

	#修飾キーのみのもの、修飾キーでないキーが複数含まれるものはダメ
	if not len(codestr)-flagCount==1:
		log.warning("%s is invalid hotkey pattern." % key)
		return False

	codestr=codestr[len(codestr)-1]
	if not codestr in keymapHandlerBase.str2key:			#存在しないキーの指定はエラー
		log.warning("keyname %s is wrong" % codestr)
		return False

	#フィルタの確認
	if filter and not filter.Check(key):
		log.warning("%s(%s): %s" % (ref,key,filter.GetLastError()))
		return False
	return keymapHandlerBase.AcceleratorEntry(flags,keymapHandlerBase.str2key[codestr],menuItemsStore.getRef(ref.upper()),ref.upper())

def permitConfrict(items,log):
	return False		#ホットキーではOSの仕様により重複登録できない


class HotkeyFilter(keymapHandlerBase.KeyFilterBase):
	def __init__(self):
		super().__init__()
		self.AddDisablePattern("WINDOWS")					#スタートメニューの表示


	def SetDefault(self,supportInputChar=False,isSystem=False,arrowCharKey=False):
		"""
			ホットキーなので、一般のソフトウェアの利用に支障を及ぼさないためにも引数は全て省略してFalseにすることを強く推奨。
		"""
		super().SetDefault(supportInputChar,isSystem,arrowCharKey)
		self.modifierKey.add("WINDOWS")

