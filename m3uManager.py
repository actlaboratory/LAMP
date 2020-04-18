import wx
import os
import datetime
import globalVars
import menuItemsStore
from views import mkDialog

#定数
LOAD_ONLY = 0
ADD = 1
REPLACE = 2

#m3uファイルロード（パス=選択ダイアログ, プレイリスト追加=置き換え）
def loadM3u(path=None, playlist=2):
    rtn = [] #ファイルパスリスト
    f = False #ファイル
    if path == None:
        fd = wx.FileDialog(None, _("プレイリストファイル選択"), wildcard=_("m3uファイル (.m3u)")+"|*.m3u|"+_("m3u8ファイル (.m3u8)")+"|*.m3u8")
        c = fd.ShowModal()
        if c == wx.ID_CANCEL: return rtn
        path = fd.GetPath()
    if os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u":
        f = open(path, "r", encoding="shift-jis")
        if playlist == 2:
            globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("UTF-8プレイリストに変換"))
            globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), True)
    elif os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u8":
        f = open(path, "r", encoding="utf-8")
        if playlist == 2:
            globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("プレイリストを上書き保存"))
            globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), True)
    if f != False: #ファイルの読み込み
        for s in f.readlines():
            s = s.strip()
            if os.path.isfile(s):
                rtn.append(s)
        f.close()
    if playlist == 2: #REPLACE
        if closeM3u() == False: return rtn #closeがキャンセルされたら中止
        globalVars.playlist.addFiles(rtn)
        globalVars.playlist.playlistFile = path
        globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U_OPEN"), True)
    elif playlist == 1: #ADD
        globalVars.playlist.addFiles(rtn)
        globalVars.playlist.playlistFile = path
    return rtn

#プレイリスト自動保存
def autoSaveM3u8():
    os.makedirs("./pl_auto_save", exist_ok=True)
    t = datetime.datetime.now()
    saveM3U8("./pl_auto_save/"+t.strftime("%Y%m%d%H%M%s.m3u8"))

#プレイリストを閉じる（）
def closeM3u():
    if globalVars.playlist.playlistFile != None:
        if loadM3u(globalVars.playlist.playlistFile, LOAD_ONLY) != globalVars.playlist.getAllFiles():
            if os.path.splitext(globalVars.playlist.playlistFile)[1] == ".m3u": #変換を確認
                d = mkDialog.Dialog()
                d.Initialize(_("プレイリスト変換確認"), _("このプレイリストは変更されています。\nm3u8ファイルに変換して保存しますか？"), (_("保存"), _("破棄"), _("キャンセル")))
                c = d.Show()
            elif os.path.splitext(globalVars.playlist.playlistFile)[1] == ".m3u8": #上書きを確認
                d = mkDialog.Dialog()
                d.Initialize(_("プレイリスト上書き保存の確認"), _("このプレイリストは変更されています。\n上書き保存しますか？"), (_("上書き"), _("破棄"), _("キャンセル")))
                c = d.Show()
            if c == 0: saveM3u8(globalVars.playlist.playlistFile, False)
            elif c == wx.ID_CANCEL: return False
    else:
        if len(globalVars.playlist.lst) != 0:
            d = mkDialog.Dialog()
            d.Initialize(_("プレイリスト保存の確認"), _("このプレイリストは変更されています。\n保存しますか？"), (_("保存"), _("破棄"), _("キャンセル")))
            c = d.Show()
            if c == 0: saveM3u8(None, False)
            elif c == wx.ID_CANCEL: return False
    globalVars.playlist.playlistFile = None
    globalVars.playlist.deleteAllFiles()
    #メニュー処理
    globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("プレイリストを上書き保存"))
    globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), False)
    globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U_CLOSE"), False)
    return True


#プレイリスト保存(保存先=参照, リロード=はい):
def saveM3u8(path=None, reload=True):
    if path != None:
        dir = os.path.dirname(path)
    if path == None or os.path.isdir(dir) == False:
        fd = wx.FileDialog(None, _("プレイリストファイル保存"), wildcard=_("m3u8ファイル (.m3u8)")+"|*.m3u8", style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        fd.ShowModal()
        path = fd.GetPath()
    path = os.path.splitext(path)[0]+".m3u8" #必ずm3u8ファイルを保存する
    with open(path, "w", encoding="utf-8") as f:
        lst = globalVars.playlist.getAllFiles()
        f.write("\n".join(lst))
    globalVars.playlist.playlistFile = path
