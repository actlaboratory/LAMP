import wx, os, multiprocessing, re, time
import globalVars, constants, view_manager, errorCodes, fxManager
from soundPlayer.bass import pybass, pytags
from views import objectDetail
from views import mkDialog
from views import mkProgress


def getTuple(lstConstant, queueDelete=False):
    if lstConstant == constants.PLAYLIST:
        return globalVars.app.hMainView.playlistView.get()
    elif lstConstant == constants.QUEUE:
        q = globalVars.app.hMainView.queueView
        ret = q.get()
        q.pop(q.getPointer())
        return ret

def previous(lstConstant):
    if not lstConstant == constants.PLAYLIST:
        t = globalVars.app.hMainView.playlistView.get()
        if t != None: return globalVars.eventProcess.play(constants.PLAYLIST)
        else: return errorCodes.END #戻しきった
    else:
        t = globalVars.app.hMainView.playlistView.getPrevious()
        if t != None: return globalVars.eventProcess.play(constants.PLAYLIST)
        else: return errorCodes.END #戻しきった

def next(lstConstant):
    t = globalVars.app.hMainView.queueView.get()
    if t != None: return globalVars.eventProcess.play(constants.QUEUE)
    else:
        t = globalVars.app.hMainView.playlistView.getNext()
        if t != None: return globalVars.eventProcess.play(constants.PLAYLIST)
        else: return errorCodes.END #進みきった

def getLCObject(lstConstant):
    if lstConstant == constants.PLAYLIST: return globalVars.app.hMainView.playlistView
    elif lstConstant == constants.QUEUE: return globalVars.app.hMainView.queueView
    else: return False

def setTag(lstConstant):
	if lstConstant == constants.PLAYLIST:
		tp = getTuple(lstConstant)
		if len(tp) >= 3: tg = getTags([tp])
		else: tg = [tp]
		lc = getLCObject(lstConstant)
		lc[lc.getPointer()] = tg[0]
	else:
		globalVars.listInfo.playingTmp = getTags([globalVars.listInfo.playingTmp])[0]
	

def getTags(tupleList):
	pl = multiprocessing.Pool()
	result = pl.apply_async(getFileInfoProcess, (tupleList,))
	while result.ready() == False: time.sleep(0.1)
	return result.get()

def getFileInfoProcess(tuples):
	pybass.BASS_Init(0, 44100, 0, 0, 0)
	pytags.TAGS_SetUTF8(True)
	#必要なプラグインを適用
	pybass.BASS_PluginLoad(b"basshls.dll", 0)
	rtn = []
	for t in tuples:
		l = list(t)
		handle = pybass.BASS_StreamCreateFile(False, l[0], 0, 0, pybass.BASS_UNICODE)
		if handle == 0:
			handle = pybass.BASS_StreamCreateURL(l[0].encode(), 0, 0, 0, 0)
		if handle == 0:
			l.extend([None, "", None, "", "", ""])
			rtn.append(tuple(l))
			continue
		if os.path.isfile(l[0]):
			size = os.path.getsize(l[0])
		else:
			size = 0
		title = pytags.TAGS_Read(handle, b"%TITL").decode("utf-8")
		lengthb = pybass.BASS_ChannelGetLength(handle, pybass.BASS_POS_BYTE)
		length = pybass.BASS_ChannelBytes2Seconds(handle, lengthb)
		artist = pytags.TAGS_Read(handle, b"%ARTI").decode("utf-8")
		album = pytags.TAGS_Read(handle, b"%ALBM").decode("utf-8")
		albumArtist = pytags.TAGS_Read(handle, b"%AART").decode("utf-8")
		pybass.BASS_StreamFree(handle)
		l.extend([size, title, length, artist, album, albumArtist])
		rtn.append(tuple(l))
	pybass.BASS_Free()
	return rtn

# 複数ファイルを追加（ファイルパスリスト, 追加先リストビュー, 追加先インデックス=末尾）
def addItems(flst, lcObj, id=-1):
	#プログレスダイアログ作成
	progress=mkProgress.Dialog("importProgressDialog")
	progress.Initialize(_("ファイルを集めています..."), _("読み込み中..."))
	progress.Show(False)
	wx.YieldIfNeeded() #プログレスダイアログを強制更新
	# 作業するファイルのリスト（ファイルパス）
	pathList = []
	# リストで受け取ってフォルダとファイルに分ける
	for s in flst:
		if progress.status == wx.CANCEL: break
		if (os.path.isfile(s) and os.path.splitext(s)[1].lower() in globalVars.fileExpansions) or re.search("^https?://.+\..+", s)!=None:
			pathList.append(s)
		else:
			_appendDirList(pathList, s)
	# 作成したファイルパスのリストから追加
	_append(pathList, lcObj, progress, id)
	view_manager.changeListLabel(lcObj)
	fxManager.load()
	progress.Destroy()

# ディレクトリパスからファイルリストを取得（ファイルパスリスト, ディレクトリパス）
def _appendDirList(lst, dir):
	# ボトムアップで探索
	dirObj = os.walk(dir, False)
	for tp in dirObj:
		if len(tp[2]) != 0:
			for file in tp[2]:
				f = tp[0] + "\\" + file
				if os.path.splitext(f)[1].lower() in globalVars.fileExpansions: lst.append(f)

# 追加
def _append(paths, lcObj, progress, id):
	lst = []
	if len(paths) == 0: return
	if id == -1: index = lcObj.GetItemCount() - 1
	addedItemCount = 0
	itemCount = len(paths)
	progPerTmp = 0
	for path in paths:
		# リストに書き込んでdataNoに+1
		fName = os.path.splitext(os.path.basename(path))[0]
		if id == -1:
			lst.append((path, fName, globalVars.listInfo.itemCounter))
		else:
			index = id+addedItemCount
			lcObj.insert(index, (path, fName, globalVars.listInfo.itemCounter))
		addedItemCount += 1
		progPer = round(addedItemCount/(itemCount/50))
		if progPer != progPerTmp:
			progress.update(addedItemCount,_("読み込み中")+"  "+str(addedItemCount)+"/"+str(itemCount),itemCount)
			wx.YieldIfNeeded() #プログレスダイアログを強制更新
		progPerTmp = progPer
		globalVars.listInfo.itemCounter += 1
		if progress.status == wx.CANCEL: return
	lcObj.extend(lst)

def infoDialog(tuple):
	if tuple[constants.ITEM_SIZE] == None or tuple[constants.ITEM_SIZE] < 0:
		size = ""
	elif tuple[constants.ITEM_SIZE] < 10**6:
		size = str(round(tuple[constants.ITEM_SIZE] / 1000, 1)) + "KB"
	elif tuple[constants.ITEM_SIZE] < 10**9:
		size = str(round(tuple[constants.ITEM_SIZE] / 10**6, 2)) + "MB"
	else:
		size = str(round(tuple[constants.ITEM_SIZE] / 10**9, 2)) + "GB"
	if tuple[constants.ITEM_LENGTH] == None or tuple[constants.ITEM_LENGTH] < 0: length = ""
	else: length = str(int(tuple[constants.ITEM_LENGTH] // 60)) + ":" + format(int(tuple[constants.ITEM_LENGTH]) // 60, "02")
	dict = {_("ァイルの場所"): tuple[constants.ITEM_PATH],
		_("ファイル名"): tuple[constants.ITEM_NAME],
		_( "ファイルサイズ"): size,
		_("タイトル"): tuple[constants.ITEM_TITLE],
		_("長さ"): length,
		_("アーティスト"): tuple[constants.ITEM_ARTIST],
		_("アルバム"): tuple[constants.ITEM_ALBUM],
		_("アルバムアーティスト"): tuple[constants.ITEM_ALBUMARTIST],
	}
	d = objectDetail.Dialog("objectDetailDialog")
	d.Initialize(dict)
	d.Show()

class listInfo():
	def __init__(self):
		self.itemCounter = 0
