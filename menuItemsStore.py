# -*- coding: utf-8 -*-
#Filer menu items store
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Note: All comments except these top lines will be written in Japanese. 

#wx のメニューのrefを一括管理してくれる便利な人
import win32file
import wx

class _MenuItemsStore(object):
	"""このクラスは、外からインスタンス化してはいけません。"""

	def __init__(self):
		self.refs={}
		self.nextID=5000

	def _getRef(self,identifier):
		identifier=identifier.upper()
		try:
			return self.refs[identifier]
		except KeyError:#なかったら作る
			ref=self.nextID
			self.nextID+=1
			self.refs[identifier]=ref
		#end なかったから作った
		return ref

_store=_MenuItemsStore()

def getRef(identifier):
	"""文字列から、対応するメニューのrefを取得する。なかったら、作ってから帰す。"""
	return _store._getRef(identifier)
