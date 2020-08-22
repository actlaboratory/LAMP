import sys, os, wx, time, winsound, re
import globalVars
from views import mkProgress

class dataDict():
	def __init__ (self):
		# dataNo:（ファイルパス, ファイル名, サイズ, タイトル, 長さ, アーティスト, アルバム, アルバムアーティスト）
		self.dict = {}
		self.dataNo = 0
	# 複数ファイルを追加（ファイルパスリスト, 追加先リスト, 対応するリストビュー, 追加先インデックス=末尾）
	def addFiles(self, flst, lst, lcObj, id=-1):
		wx.CallAfter(self.addFilesCall, flst,lst,lcObj,id)

	#ファイル追加（ファイルパスリスト, 追加先リスト, リストビュー, 追加先インデックス=末尾）
	def addFilesCall(self, flst, lst, lcObj, id=-1):
		#プログレスダイアログ作成
		progress=mkProgress.Dialog()
		progress.Initialize(_("ファイルを集めています..."), _("読み込み中..."))
		progress.Show(False)
		globalVars.app.Yield()
		# 作業するファイルのリスト（ファイルパス）
		pathList = []
		# リストで受け取ってフォルダとファイルに分ける
		for s in flst:
			if (os.path.isfile(s) and os.path.splitext(s) == ".mp3") or re.search("^https?://.+\..+", s)!=None:
				pathList.append(s)
			else:
				self.appendDirList(pathList, s)
		# 作成したファイルパスのリストから辞書に追加
		self.appendDict(pathList, lst, lcObj, progress, id)
		progress.Destroy()
		winsound.Beep(3000, 100)
		winsound.Beep(4000, 100)
		winsound.Beep(5000, 100)

	# ディレクトリパスからファイルリストを取得（ファイルパスリスト, ディレクトリパス）
	def appendDirList(self, lst, dir):
		# ボトムアップで探索
		dirObj = os.walk(dir, False)
		for tp in dirObj:
			if len(tp[2]) != 0:
				for file in tp[2]:
					f = tp[0] + "\\" + file
					if os.path.splitext(f)[1] == ".mp3": lst.append(f)

	# 辞書作成
	def appendDict(self, paths, lst, lcObj, progress, id):
		if len(paths) == 0: return
		if id == -1: index = lcObj.GetItemCount() - 1
		addedItemCount = 0
		itemCount = len(paths)
		progPerTmp = 0
		for path in paths:
			# 辞書とリストに書き込んでdataNoに+1
			fName = os.path.splitext(os.path.basename(path))[0]
			self.dict[self.dataNo] = (path, fName)
			if id == -1:
				lst.appendF((path, self.dataNo))
				index = lcObj.Append([fName])
			else:
				index = id+addedItemCount
				lst.addF(index, (path, self.dataNo))
				lcObj.InsertItem(index, fName)
			lcObj.SetItemData(index, self.dataNo)
			addedItemCount += 1
			progPer = round(addedItemCount/(itemCount/50))
			if progPer != progPerTmp:
				progress.update(addedItemCount,_("読み込み中")+"  "+str(addedItemCount)+"/"+str(itemCount),itemCount)
				globalVars.app.Yield(True) #プログレスダイアログを強制更新
			progPerTmp = progPer
			self.dataNo += 1
