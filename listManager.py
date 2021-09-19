# list utils for LAMP
# Copyright (C) 2020-2021 Hiroki Fujii <hfujii@hisystron.com>

import wx, os, multiprocessing, re, time, threading
import configparser
import globalVars, constants, view_manager, errorCodes, fxManager
from soundPlayer.bass import pybass, pytags
from views import objectDetail
from views import mkProgress
from views import loadErrorDialog

lock = threading.Lock()

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
    globalVars.app.hMainView.queueView.setPointer(-1)
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
    if len(tupleList) == 1 and len(tupleList[0]) > 3:
        return tupleList
    pl = multiprocessing.Pool()
    result = pl.apply_async(getFileInfoProcess, (tupleList,))
    while result.ready() == False: time.sleep(0.1)
    return result.get()

def getFileInfoProcess(tuples):
    pybass.BASS_Init(0, 44100, 0, 0, 0)
    #pytags.TAGS_SetUTF8(True)
    #必要なプラグインを適用
    pybass.BASS_PluginLoad(b"basshls.dll", 0)
    rtn = []
    for t in tuples:
        l = list(t)
        if len(l) > 3:
            rtn.append(tuple(l))
            continue
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
        lengthb = pybass.BASS_ChannelGetLength(handle, pybass.BASS_POS_BYTE)
        length = pybass.BASS_ChannelBytes2Seconds(handle, lengthb)
        # 文字関係取得
        for charCode in ["cp932", "utf-8", ""]:
            if charCode == "":
                title, artist, album, albumArtist = "", "", "", ""
            else:
                try:
                    title = pytags.TAGS_Read(handle, b"%TITL").decode(charCode)
                    artist = pytags.TAGS_Read(handle, b"%ARTI").decode(charCode)
                    album = pytags.TAGS_Read(handle, b"%ALBM").decode(charCode)
                    albumArtist = pytags.TAGS_Read(handle, b"%AART").decode(charCode)
                    break
                except UnicodeDecodeError as e: continue

        pybass.BASS_StreamFree(handle)
        l.extend([size, title, length, artist, album, albumArtist])
        rtn.append(tuple(l))
    pybass.BASS_Free()
    return rtn

# 複数ファイルを追加（ファイルパスリスト, 追加先リストビュー, 追加先インデックス=末尾, エラー無視=False）
def addItems(flst, lcObj, id=-1, ignoreError=False):
    progress=mkProgress.Dialog("importProgressDialog")
    progress.Initialize(_("ファイルを集めています..."), _("読み込み中..."))
    progress.Show(False)
    t = threading.Thread(target=addItemsThread, args=(progress, flst, lcObj, id, ignoreError))
    t.start()

def addItemsThread(progress, flst, lcObj, id=-1, ignoreError=False):
    with lock:
        # 作業するファイルのリスト（ファイルパス）
        pathList = []
        errorList = []
        notFoundList = []
        # リストで受け取ってフォルダとファイルに分ける
        for s in flst:
            if progress.status == wx.CANCEL: break
            if os.path.isfile(s) and os.path.splitext(s)[1].lower() in globalVars.fileExpansions:
		        # フィルタによる除外処理
                if not globalVars.filter.test(s):
                    continue
                pathList.append(s)
            elif re.search("^https?://.+\..+/.*$", s)!=None:
                pathList.append(s)
            elif os.path.isfile(s) and os.path.splitext(s)[1].lower() == ".url":
                try: 
                    configP = configparser.ConfigParser()
                    configP.read(s)
                    url = configP["InternetShortcut"]["url"]
                    if re.search("^https?://.+\..+/.*$", url)!=None: pathList.append(url)
                except: pass
            elif os.path.isdir(s):
                _appendDirList(pathList, s, errorList)
            elif os.path.isfile(s):
                errorList.append(s)
            else:
                notFoundList.append(s)
        # 作成したファイルパスのリストから追加
        if len(lcObj) == 0: _append(pathList, lcObj, progress, -1)
        else: _append(pathList, lcObj, progress, id)
        view_manager.changeListLabel(lcObj)
        if (len(errorList) != 0 or len(notFoundList) != 0) and ignoreError==False:
            wx.CallAfter(loadErrorDialog.run, errorList, notFoundList)
        fxManager.load()
        wx.CallAfter(progress.Destroy)

# ディレクトリパスからファイルリストを取得（ファイルパスリスト, ディレクトリパス, 非対応格納リスト）
def _appendDirList(lst, dir, errorList):
    # ボトムアップで探索
    dirObj = os.walk(dir, False)
    for tp in dirObj:
        if len(tp[2]) != 0:
            for file in tp[2]:
                f = tp[0] + "\\" + file
                if os.path.splitext(f)[1].lower() in globalVars.fileExpansions:
                    # フィルタによる除外処理
                    if not globalVars.filter.test(f):
                        continue
                    lst.append(f)
                else: errorList.append(f)

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
        fName = re.sub(r"^([0-9]{1,2}-)?[0-9]{2} (- )?", "", os.path.splitext(os.path.basename(path))[0])
        if id == -1:
            lst.append((path, fName, globalVars.listInfo.itemCounter))
        else:
            index = id+addedItemCount
            lcObj.insert(index, (path, fName, globalVars.listInfo.itemCounter))
        addedItemCount += 1
        progPer = round(addedItemCount/(itemCount/50))
        if progPer != progPerTmp:
            wx.CallAfter(progress.update, addedItemCount,_("読み込み中")+"  "+str(addedItemCount)+"/"+str(itemCount),itemCount)
            wx.CallAfter(wx.YieldIfNeeded)
            #wx.YieldIfNeeded() #プログレスダイアログを強制更新
        progPerTmp = progPer
        globalVars.listInfo.itemCounter += 1
        if progress.status == wx.CANCEL: 
            lcObj.extend(lst)
            return
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
    else:
        hour = int(tuple[constants.ITEM_LENGTH] // 3600)
        min = int((tuple[constants.ITEM_LENGTH] - hour * 3600) // 60)
        sec = int((tuple[constants.ITEM_LENGTH] - hour * 3600 - min * 60))
        length = str(hour) + ":" + format(min, "02") + ":" + format(sec, "02")
    dict = {_("ファイルの場所"): tuple[constants.ITEM_PATH],
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
        self.playingTmp=None
        self.playlistFile = None