import os, globalVars

class listBase():
	def __init__(self):
		self. lst = []
		self.playIndex = -1
		self.isDeletePlayingFile = 0

	def setListCtrl(self, obj):
		self.lcObject = obj

	def positionReset(self):
		self.playIndex = -1

	# ファイル追加（外部から呼び出し）
	def addFiles(self, pathLst, index=-1):
		if index >= 0 and index < len(self.lst):
			globalVars.listManage.addFiles(pathLst, self, self.lcObject, index)
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

	def deleteFile(self, index):
		if index >= 0 and index < self.playIndex:
			self.playIndex -= 1
			rtn = self.lst.pop(index)
			self.lcObject.DeleteItem(index)
		# 再生中のファイルを削除したときのフラグ処理
		elif index == self.playIndex:
			isDeletePlayingFile =1
			rtn = self.lst.pop(index)
			self.lcObject.DeleteItem(index)
		elif index > self.playIndex and index < len(self.lst):
			rtn = self.lst.pop(index)
			self.lcObject.DeleteItem(index)
		return rtn

	# 任意のファイルを取得（インデックス=最終getFile, 再生位置移動=しない）
	def getFile(self, index=-2, movePos=False):
		#インデックス指定の呼び出しに削除後の処理は考慮しない
		if index >= 0 and index < len(self.lst):
			self. isDeletePlayingFile = 0
			rtn = self.lst[index]
		elif index == -1 and len(self.lst) != 0:
			self. isDeletePlayingFile = 0
			index = len(self.lst)-1
			rtn = self.lst[index]
		# 第2引数なし（-2）で、再生中のファイルを返す
		elif index == -2 and self.playIndex >= 0 and self.playIndex < len(self.lst):
			if self.isDeletePlayingFile == 1:
				rtn = None
			else:
				rtn = self.lst[self.playIndex]
		# 再生位置リセット状態でも None を返す
		else:
			rtn = None
		if rtn != None and index >= 0 and movePos == True:
			self.playIndex = index
			return rtn
		else:
			return rtn

	def getPrevious(self):
		# 前回再生中ファイルが削除されているときは自ファイル
		if self.isDeletePlayingFile == 1:
			return self.getFile()
		if self.playIndex >= 0:
			self.playIndex -= 1
			# 戻る操作では再生位置のリセットは行わない
			if self.playIndex == -1:
				self.playIndex = 0
				return None
			return self.lst[self.playIndex]
		else:
			return None

class playlist(listBase):
	def getNext(self):
		if self.isDeletePlayingFile == 1:
			return self.getFile()
		if self.playIndex < len(self.lst)-1:
			self.playIndex += 1
			return self.lst[self.playIndex]
		else:
			return None

class queue(listBase):
	def getNext(self):
		if len(self.lst) > 0:
			return self.deleteFile(0)
		else:
			return None
