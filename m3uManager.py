# Copyright (C) 2020_2021 Hiroki Fujii <hfujii@hisystron.com>

import wx
import os
import pickle
import history
import datetime
import fxManager
import globalVars
import menuItemsStore
import listManager
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
        fd = wx.FileDialog(None, _("プレイリストファイル選択"), wildcard=_("プレイリストファイル (.m3u8/.m3u)")+"|*.m3u8*;*.m3u")
        c = fd.ShowModal()
        if c == wx.ID_CANCEL: return rtn
        path = fd.GetPath()
    if os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u":
        f = open(path, "r", encoding="shift-jis")
    elif os.path.isfile(path) and os.path.splitext(path)[1] == ".m3u8":
        f = open(path, "r", encoding="utf-8")
    if f != False: #ファイルの読み込み
        for s in f.readlines():
            s = s.strip()
            if os.path.isfile(s):
                rtn.append(s)
        f.close()
    else:
        ed = mkDialog.Dialog("m3uLoadErrorDialog")
        ed.Initialize(_("読み込みエラー"), _("プレイリストファイルの読み込みに失敗しました。"), ("OK",), sound=False)
        fxManager.error()
        return ed.Show()
    if playlist == 2: #REPLACE
        if closeM3u() == False: return rtn #closeがキャンセルされたら中止
        listManager.addItems(rtn, globalVars.app.hMainView.playlistView)
        globalVars.listInfo.playlistFile = path
        globalVars.m3uHistory.add(path)
        globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U_OPEN"), True)
        globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U_CLOSE"), True)
    elif playlist == 1: #ADD
        listManager.addItems(rtn, globalVars.app.hMainView.playlistView)
        globalVars.listInfo.playlistFile = path
        globalVars.m3uHistory.add(path)
    if os.path.splitext(globalVars.listInfo.playlistFile)[1] == ".m3u":
        if playlist == 2:
            globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("UTF-8プレイリストに変換"))
            globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), True)
            globalVars.app.hMainView.menu.hPlaylistMenu.Enable(menuItemsStore.getRef("SET_STARTUPLIST"), True)
    elif os.path.splitext(globalVars.listInfo.playlistFile)[1] == ".m3u8":
        if playlist == 2:
            globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("プレイリストを上書き保存"))
            globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), True)
            globalVars.app.hMainView.menu.hPlaylistMenu.Enable(menuItemsStore.getRef("SET_STARTUPLIST"), True)
    return rtn

#プレイリスト自動保存
def autoSaveM3u8():
    os.makedirs("./pl_auto_save", exist_ok=True)
    t = datetime.datetime.now()
    saveM3U8("./pl_auto_save/"+t.strftime("%Y%m%d%H%M%s.m3u8"))

#プレイリストを閉じる（）
def closeM3u():
    if globalVars.listInfo.playlistFile != None:
        lst = []
        for t in globalVars.app.hMainView.playlistView:
            lst.append(t[0])
        if loadM3u(globalVars.listInfo.playlistFile, LOAD_ONLY) != lst:
            if os.path.splitext(globalVars.listInfo.playlistFile)[1] == ".m3u": #変換を確認
                d = mkDialog.Dialog("m3uConversionConfirmDialog")
                d.Initialize(_("プレイリスト変換確認"), _("このプレイリストは変更されています。\nm3u8ファイルに変換して保存しますか？"), (_("保存"), _("破棄"), _("キャンセル")), sound=False)
                fxManager.confirm()
                c = d.Show()
            elif os.path.splitext(globalVars.listInfo.playlistFile)[1] == ".m3u8": #上書きを確認
                d = mkDialog.Dialog("m3uOverwriteConfirmDialog")
                d.Initialize(_("プレイリスト上書き保存の確認"), _("このプレイリストは変更されています。\n上書き保存しますか？"), (_("上書き"), _("破棄"), _("キャンセル")), sound=False)
                fxManager.confirm()
                c = d.Show()
            if c == 0: saveM3u8(globalVars.listInfo.playlistFile, False)
            elif c == wx.ID_CANCEL: return False
    else:
        if len(globalVars.app.hMainView.playlistView) != 0:
            d = mkDialog.Dialog("m3uSaveConfirmDialog")
            d.Initialize(_("プレイリスト保存の確認"), _("このプレイリストは変更されています。\n保存しますか？"), (_("保存"), _("破棄"), _("キャンセル")), sound=False)
            fxManager.confirm()
            c = d.Show()
            if c == 0: saveM3u8(None, False)
            elif c == wx.ID_CANCEL: return False
    # 停止して削除
    globalVars.eventProcess.stop()
    globalVars.listInfo.playlistFile = None
    globalVars.app.hMainView.playlistView.clear()
    #メニュー処理
    globalVars.app.hMainView.menu.hFileMenu.SetLabel(menuItemsStore.getRef("M3U8_SAVE"), _("プレイリストを上書き保存"))
    globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U8_SAVE"), False)
    globalVars.app.hMainView.menu.hFileMenu.Enable(menuItemsStore.getRef("M3U_CLOSE"), False)
    globalVars.app.hMainView.menu.hPlaylistMenu.Enable(menuItemsStore.getRef("SET_STARTUPLIST"), False)
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
        lst = []
        for p in globalVars.app.hMainView.playlistView:
            lst.append(p[0])
        f.write("\n".join(lst))
    globalVars.listInfo.playlistFile = path
    globalVars.m3uHistory.add(path)

def loadHistory():
    ret = history.History(20, False)
    if os.path.isfile("m3u_history.dat"):
        f = open("m3u_history.dat", "rb")
        hList = pickle.load(f)
        if type(hList) is list:
            ret.lst = hList
            ret.cursor = len(hList) - 1
        f.close()
    return ret

def dumpHistory():
    f = open("m3u_history.dat", "wb")
    pickle.dump(globalVars.m3uHistory.getList(), f)
    f.close()

