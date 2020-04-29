import sys, os, wx, time, winsound, re
import threading
import globalVars
from views import mkProgress

def is64Bit():
	return sys.maxsize > 2 ** 32

#使用環境に応じて適切なdllをロード
if is64Bit():
	from pybass64 import pybass
	from pybass64 import pytags
else:
	from pybass import pybass
	from pybass import pytags

class dataDict():
	def __init__ (self):
		pytags.TAGS_SetUTF8(True)
		# dataNo:（ファイルパス, ファイル名, サイズ, タイトル, 長さ, アーティスト, アルバム, アルバムアーティスト）
		self.dict = {}
		self.dataNo = 0
		# 表示する項目（タプルのインデックス）
		self.showValue = 3

	# 複数ファイルを追加（ファイルパスリスト, 追加先リスト, 対応するリストビュー, 追加先インデックス=末尾）
	def addFiles(self, flst, lst, lcObj, id=-1):
		#プログレスダイアログ作成
		progress=mkProgress.Dialog()
		progress.Initialize(_("ファイルを集めています..."), _("読み込み中..."))
		t1 = threading.Thread(target=self.addFilesThread,args=(flst,lst,lcObj,progress,id))
		t1.start()

	#ファイル追加スレッド（ファイルパスリスト, 追加先リスト, リストビュー, プログレスダイアログ）
	def addFilesThread(self, flst, lst, lcObj, progress, id=-1):
		# 作業するファイルのリスト（ファイルパス）
		pathList = []
		t2 = threading.Thread(target=progress.Show)
		t2.start() # プログレスダイアログ表示
		# リストで受け取ってフォルダとファイルに分ける
		for s in flst:
			if os.path.isfile(s) == True or re.search("https?://.+\..+", s)!="":
				pathList.append(s)
			else:
				self.appendDirList(pathList, s)
		# 作成したファイルパスのリストから辞書に追加
		self.appendDict(pathList, lst, lcObj, progress, id)
		winsound.Beep(4000, 1000)


	# ディレクトリパスからファイルリストを取得（ファイルパスリスト, ディレクトリパス）
	def appendDirList(self, lst, dir):
		# ボトムアップで探索
		dirObj = os.walk(dir, False)
		for tp in dirObj:
			if len(tp[2]) != 0:
				for file in tp[2]:
					f = tp[0] + "\\" + file
					lst.append(f)

	# 辞書作成
	def appendDict(self, paths, lst, lcObj, progress, id):
		addedItemCount = 0
		itemCount = len(paths)
		if itemCount>0:progress.update(0,_("読み込み中")+"  0/"+str(itemCount),itemCount)
		for path in paths:
			handle = pybass.BASS_StreamCreateFile(False, path, 0, 0, pybass.BASS_UNICODE)
			if handle == 0:
				handle = pybass.BASS_StreamCreateURL(path.encode(), 0, 0, 0, 0)
				if handle == 0:
					print("not supported")
					itemCount -= 1
					continue
			# ファイル情報取得
			fName = os.path.basename(path)
			if os.path.isfile(path):
				size = os.path.getsize(path)
			else:
				size = 0
			title = pytags.TAGS_Read(handle, b"%TITL").decode("utf-8")
			lengthb = pybass.BASS_ChannelGetLength(handle, pybass.BASS_POS_BYTE)
			length = pybass.BASS_ChannelBytes2Seconds(handle, lengthb)
			artist = pytags.TAGS_Read(handle, b"%ARTI").decode("utf-8")
			album = pytags.TAGS_Read(handle, b"%ALBM").decode("utf-8")
			albumArtist = pytags.TAGS_Read(handle, b"%AART").decode("utf-8")
			pybass.BASS_StreamFree(handle)

			# 辞書とリストビューに書き込んでdataNoに+1
			self.dict[self.dataNo] = (path, fName, size, title, length, artist, album, albumArtist)
			label = self.dict[self.dataNo][self.showValue]
			if id == -1:
				lst.appendF((path, self.dataNo))
				index = lcObj.Append([label])
			else:
				index = id+addedItemCount
				lst.addF(index, (path, self.dataNo))
				lcObj.InsertItem(index, label)
			lcObj.SetItemData(index, self.dataNo)
			addedItemCount += 1
			if addedItemCount!=0 and int(itemCount/100)!=0:
				if addedItemCount%int(itemCount/100)==0: #プログレス更新
					progress.update(addedItemCount,_("読み込み中")+"  "+str(addedItemCount)+"/"+str(itemCount),itemCount)
			self.dataNo += 1
		globalVars.app.hMainView.hFrame.Enable()
		progress.Destroy()


