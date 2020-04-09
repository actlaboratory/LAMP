import wx
import os
import globalVars

#定数
LOAD_ONLY = 0
ADD = 1
REPLACE = 2

#m3uファイルロード（パス=選択ダイアログ, プレイリスト追加=置き換え）
def loadM3u(path=None, playlist=2):
    f = False #ファイル
    if path == None:
        fd = wx.FileDialog(None, _("プレイリストファイル選択"), wildcard=_("m3uファイル (.m3u)")+"|*.m3u|"+_("m3u8ファイル (.m3u8)")+"|*.m3u8")
        fd.ShowModal()
        path = fd.GetPath()
    if os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u":
        f = open(path, "r", encoding="shift-jis")
        rtn = [] #ファイルパスリスト
    elif os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u8":
        f = open(path, "r", encoding="utf-8")
    if f != False: #ファイルの読み込み
        for s in f.readlines():
            s = s.strip()
            if os.path.isfile(s):
                rtn.append(s)
        f.close()
    if playlist == 2: #REPLACE
        globalVars.playlist.deleteAllFiles()
        globalVars.playlist.addFiles(rtn)
    elif playlist == 1: #ADD
        globalVars.playlist.addFiles(rtn)
    return rtn