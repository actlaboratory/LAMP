import os, globalVars

class listBase():
	def __init__(self):
		self. lst = [] #(ファイルパス, データ連番)
		self.playIndex = -1
		self.isDeletePlayingFile = 0

	def setListCtrl(self, obj):
		self.lcObject = obj

	def positionReset(self):
		self.playIndex = -1

	# ファイル追加（外部から呼び出し）
	def addFiles(self, pathLst, index=-1):
		if index >= 0 and index < len(self.lst):
			globalVars.dataDict.addFiles(pathLst, self, self.lcObject, index)
		elif index == -1:
			globalVars.dataDict.addFiles(pathLst, self, self.lcObject)

	def appendF(self,fileName):
		self.lst.append(fileName)

	def addF(self, index, fileName):
		# 再生中と手前に追加する処理
		if index >= 0 and index <= self.playIndex:
			self.playIndex += 1
			self.lst.insert(index, fileName)
		# 再生中より後に追加
		elif index > self.playIndex and index < len(self.lst):
			self.lst.insert(index, fileName)

	# 全消去
	def deleteAllFiles(self):
		if self.deleteFile(0) != (None, None):
			self.deleteAllFiles()
		self.playIndex = -1

	def deleteFile(self, index):
		rtn = (None, None) #戻り値の初期化
		if index >= 0 and index <= self.playIndex:
			#再生中ファイルの再生完了処理は呼び出し元が行う。
			self.playIndex -= 1
			rtn = self.lst.pop(index)
			self.lcObject.DeleteItem(index)
			del globalVars.dataDict.dict[rtn[1]]
		elif index > self.playIndex and index < len(self.lst):
			rtn = self.lst.pop(index)
			self.lcObject.DeleteItem(index)
			del globalVars.dataDict.dict[rtn[1]]
		return rtn

	#全ファイルのリストを取得
	def getAllFiles(self):
		rtn = []
		for t in self.lst:
			rtn.append(t[0])
		return rtn

	#（ファイル, 固有値）からファイルパス取得（データ, 再生位置移動=する）
	def getIndex(self, tpl):
		try:
			return self.lst.index(tpl)
		except ValueError:
			return None

	# インデックスから（ファイル,固有値）を取得（インデックス=現在ファイル）
	def getFile(self, index=-2):
		if index >= -1 and index < len(self.lst) and len(self.lst) != 0:
			return self.lst[index]
		#引数なし（-2）で、再生中のファイルを返す
		elif index == -2 and self.playIndex >= 0 and self.playIndex < len(self.lst):
			return self.lst[self.playIndex]
		# その他、None を返す
		else:
			return (None, None)

class playlist(listBase):
	def __init__(self):
		super().__init__()
		self.playlistFile = None

	def getPrevious(self):
		if self.playIndex > 0 and self.playIndex < len(self.lst):
			return self.lst[self.playIndex-1]
		else:
			return ((None, None))


	def getNext(self):
		if self.playIndex < len(self.lst)-1:
			return self.lst[self.playIndex+1]
		else:
			return (None, None)

class queue(listBase):
	def getNext(self):
		if len(self.lst) != 0:
			return self.lst[0]
		else:
			return (None, None)
