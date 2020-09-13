import sys, os, wx, time, winsound, re, multiprocessing
import globalVars
from views import mkProgress
from soundPlayer.bass import pybass, pytags
from views import objectDetail

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
			if (os.path.isfile(s) and os.path.splitext(s)[1] == ".mp3") or re.search("^https?://.+\..+", s)!=None:
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
			self.dict[self.dataNo] = [path, fName]
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

	def getTags(self, dataNoList):
		pathList = []
		for i in range(len(dataNoList)):
			try:
				while len(self.dict[dataNoList[i]]) > 2: dataNoList.pop(i)
			except IndexError as e:
				break
		if len(dataNoList) == 0: return
		for num in dataNoList:
			pathList.append(self.dict[num][0])
		pl = multiprocessing.Pool()
		result = pl.apply_async(getFileInfoProcess, (pathList,))
		while result.ready() == False: time.sleep(0.1)
		info = result.get()
		i = 0
		for num in dataNoList:
			if len(self.dict[num]) == 2: self.dict[num] += info[i]
			i += 1

def getFileInfoProcess(paths):
	pybass.BASS_Init(0, 44100, 0, 0, 0)
	pytags.TAGS_SetUTF8(True)
	#必要なプラグインを適用
	pybass.BASS_PluginLoad(b"basshls.dll", 0)
	rtn = []
	for path in paths:
		handle = pybass.BASS_StreamCreateFile(False, path, 0, 0, pybass.BASS_UNICODE)
		if handle == 0:
			handle = pybass.BASS_StreamCreateURL(path.encode(), 0, 0, 0, 0)
		# ファイル情報取得
		fName = os.path.basename(path)
		if handle == 0:
			rtn.append([None, "", None, "", "", ""])
			continue
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
		rtn.append([size, title, length, artist, album, albumArtist])
	pybass.BASS_Free()
	return tuple(rtn)

def infoDialog(dataNo):
	ft = globalVars.dataDict.dict[dataNo]
	if ft[2] == None or ft[2] < 0:
		size = ""
	elif ft[2] < 10**6:
		size = str(round(ft[2] / 1000, 1)) + "KB"
	elif ft[2] < 10**9:
		size = str(round(ft[2] / 10**6, 2)) + "MB"
	else:
		size = str(round(ft[2] / 10**9, 2)) + "GB"
	if ft[4] == None or ft[2] < 0: length = ""
	else: length = str(int(ft[4] // 60)) + ":" + format(int(ft[4]) // 60, "02")
	dict = {_("ァイルの場所"): ft[0],
		_("ファイル名"): ft[1],
		_( "ファイルサイズ"): size,
		_("タイトル"): ft[3],
		_("長さ"): length,
		_("アーティスト"): ft[5],
		_("アルバム"): ft[6],
		_("アルバムアーティスト"): ft[7]
	}
	d = objectDetail.Dialog()
	d.Initialize(dict)
	d.Show()

