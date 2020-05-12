import sys, os, wx, time, winsound, re
import multiprocessing
import copy
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
		# dataNo:（ファイルパス, ファイル名, サイズ, タイトル, 長さ, アーティスト, アルバム, アルバムアーティスト）
		self.dict = {}
		self.dataNo = 0
		# 表示する項目（タプルのインデックス）
		self.showValue = 3

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
			if os.path.isfile(s) == True or re.search("^https?://.+\..+", s)!=None:
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
					lst.append(f)

	# 辞書作成
	def appendDict(self, paths, lst, lcObj, progress, id):
		if len(paths) == 0: return
		if id == -1: index =lcObj.GetItemCount() - 1
		addedItemCount = 0
		itemCount = len(paths)
		#リストを分割
		split = itemCount // 1000
		pathGroup = [] #分割したリスト
		for i in range(0, split+1):
			if i == split:
				pathGroup.append(paths[i*1000:])
			else:
				pathGroup.append(paths[i*1000:(i+1)*1000])

		pl = multiprocessing.Pool()
		result = [] #結果を入れるリスト
		for path in pathGroup:
			result.append(pl.apply_async(getFileInfoProcess, (path,)))

		for o in result:
			while o.ready() == False:
				time.sleep(1)
			infos = o.get()
			for info in infos:
				# 辞書とリストに書き込んでdataNoに+1
				if info == None:
					itemCount -= 1
					continue
				self.dict[self.dataNo] = copy.deepcopy(info)
				label = self.dict[self.dataNo][self.showValue]
				if id == -1:
					lst.appendF((self.dict[self.dataNo][0], self.dataNo))
					index = lcObj.Append([label])
				else:
					index = id+addedItemCount
					lst.addF(index, (self.dict[self.dataNo][0], self.dataNo))
					lcObj.InsertItem(index, label)
				lcObj.SetItemData(index, self.dataNo)
				addedItemCount += 1
				if addedItemCount%10 == 0:	progress.update(addedItemCount,_("読み込み中")+"  "+str(addedItemCount)+"/"+str(itemCount),itemCount)
				self.dataNo += 1
			globalVars.app.Yield(True) #プログレスダイアログを強制更新
		pl.close() #マルチプロセス終了


def getFileInfoProcess(paths):
	pybass.BASS_Init(0, 44100, 0, 0, 0)
	pytags.TAGS_SetUTF8(True)
	rtn = []
	for path in paths:
		handle = pybass.BASS_StreamCreateFile(False, path, 0, 0, pybass.BASS_UNICODE)
		if handle == 0:
			handle = pybass.BASS_StreamCreateURL(path.encode(), 0, 0, 0, 0)
			if handle == 0:
				print("not supported")
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
		rtn.append((path, fName, size, title, length, artist, album, albumArtist))
	pybass.BASS_Free()
	return tuple(rtn)
