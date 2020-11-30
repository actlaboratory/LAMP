import wx
import globalVars
import context_menus
import constants
import defaultKeymap
import keymap
import listManager

# ビットマップボタンの構成
def setBitmapButton(button, backgroundWindow, bitmap, label):
	if backgroundWindow != None: button.SetBackgroundColour(backgroundWindow.GetBackgroundColour())
	button.SetBitmap(bitmap)
	button.SetLabel(label)
	button.setToolTip()

# イベントバインド関数
def listViewSetting(lc, identifier):
	lc.AppendColumn("")
	lc.SetDropTarget(fileDrop(lc))
	lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, globalVars.eventProcess.listActivate)
	lc.Bind(wx.EVT_CONTEXT_MENU, context_menus.contextMenuOnListView)

	"""acceleratorTable登録準備"""
	keymaping=keymap.KeymapHandler(defaultKeymap.defaultKeymap)
	t = keymaping.GetTable(identifier)
	lc.SetAcceleratorTable(t)

	#自動リサイズ
	lc.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
	lc.Bind(wx.EVT_SIZE, resizeEvent)

	globalVars.popupMenu4listView = context_menus.setContextMenu(lc, identifier)


# リストコントロールのラベルを変更
def changeListLabel(lc):
	if lc == globalVars.app.hMainView.playlistView:
		globalVars.app.hMainView.playlistLabel.SetLabel(_("プレイリスト") + " (" + str(lc.GetItemCount()) + _("件") + ")")
	elif lc == globalVars.app.hMainView.queueView:
		globalVars.app.hMainView.queueLabel.SetLabel(_("キュー") + " (" + str(lc.GetItemCount()) + _("件") + ")")

def resizeEvent(evt): #リサイズイベント処理
	evt.GetEventObject().SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)



# ドラッグアンドドロップクラス
class fileDrop(wx.FileDropTarget):
	def __init__(self, window):
		super().__init__()
		self.window = window
		
	def OnDropFiles(self, x, y, files):
		if self.window == globalVars.app.hMainView.playlistView or self.window == globalVars.app.hMainView.queueView:
			listManager.addItems(files, self.window)
		return True

def setValueShadowList(l):
	l.Append(_("ファイル名"))
	l.Append(_("場所"))
	l.Append(_("タイトル"))
	l.Append(_("アルバム"))
	l.Append(_("アーティスト"))
	l.Append(_("アルバムアーティスト"))
	l.Append(_("合計"))
	l.Append(_("経過時間を確認するには Ctrl + T を押します"))

def setFileStaticInfoView():
	l = globalVars.app.hMainView.shadowList
	if globalVars.eventProcess.playingList == constants.PLAYLIST: t = listManager.getTuple(constants.PLAYLIST)
	else: t = globalVars.listInfo.playingTmp
	l.SetString(0, _("ファイル名") + ":" + t[constants.ITEM_NAME])
	l.SetString(1, _("場所") + ":" + t[constants.ITEM_PATH])
	l.SetString(2, _("タイトル") + ":" + t[constants.ITEM_TITLE])
	l.SetString(3, _("アルバム") + ":" + t[constants.ITEM_ALBUM])
	l.SetString(4, _("アーティスト") + ":" + t[constants.ITEM_ARTIST])
	l.SetString(5, _("アルバムアーティスト") + ":" + t[constants.ITEM_ALBUMARTIST])
	if t[constants.ITEM_LENGTH] == None: length = ""
	else:
		hour = t[constants.ITEM_LENGTH] // 3600
		min = (t[constants.ITEM_LENGTH] - hour * 3600) // 60
		sec = t[constants.ITEM_LENGTH] - hour * 3600 - min * 60
		if hour == 0: sHour = ""
		else: sHour = str(int(hour)) + _("時間") + " "
		if min == 0: sMin = ""
		else: sMin = str(int(min)) + _("分") + " "
		if sec == 0: sSec = ""
		else: sSec = str(int(sec)) + _("秒")
		length = sHour + sMin + sSec
	l.SetString(6, _("合計") + ":" + length)
	if t[constants.ITEM_TITLE] != "": globalVars.app.hMainView.hFrame.SetTitle("LAMP - " + str(t[constants.ITEM_TITLE]))
	else: globalVars.app.hMainView.hFrame.SetTitle("LAMP - " + str(t[constants.ITEM_NAME]))

def clearStaticInfoView():
	l = globalVars.app.hMainView.shadowList
	l.SetString(0, _("ファイル名"))
	l.SetString(1, _("場所"))
	l.SetString(2, _("タイトル"))
	l.SetString(3, _("アルバム"))
	l.SetString(4, _("アーティスト"))
	l.SetString(5, _("アルバムアーティスト"))
	l.SetString(6, _("合計"))
	globalVars.app.hMainView.hFrame.SetTitle("LAMP")


# ボタン制御
def buttonSetPlay():
	setBitmapButton(globalVars.app.hMainView.playPauseBtn, None, wx.Bitmap("./resources/play.dat", wx.BITMAP_TYPE_GIF), _("再生"))

def buttonSetPause():
	wx.CallAfter(setBitmapButton, globalVars.app.hMainView.playPauseBtn, None, wx.Bitmap("./resources/pause.dat", wx.BITMAP_TYPE_GIF), _("一時停止"))

def buttonSetRepeatLoop():
	setBitmapButton(globalVars.app.hMainView.repeatLoopBtn, None, wx.Bitmap("./resources/repeatLoop.dat", wx.BITMAP_TYPE_GIF), _("リピートに切り替える"))

def buttonSetRepeat():
	setBitmapButton(globalVars.app.hMainView.repeatLoopBtn, None, wx.Bitmap("./resources/repeat_on.dat", wx.BITMAP_TYPE_GIF), _("ループに切り替える"))

def buttonSetLoop():
	setBitmapButton(globalVars.app.hMainView.repeatLoopBtn, None, wx.Bitmap("./resources/loop_on.dat", wx.BITMAP_TYPE_GIF), _("リピートとループを解除する"))

def buttonSetShuffleOff():
	setBitmapButton(globalVars.app.hMainView.shuffleBtn, None, wx.Bitmap("./resources/shuffle_off.dat", wx.BITMAP_TYPE_GIF), _("シャッフルをオンにする"))

def buttonSetShuffleOn():
	setBitmapButton(globalVars.app.hMainView.shuffleBtn, None, wx.Bitmap("./resources/shuffle_on.dat", wx.BITMAP_TYPE_GIF), _("シャッフルをオフにする"))

def buttonSetMuteOff():
	if globalVars.app.config.getstring("view","colorMode","white",("white","dark")) == "white":
		setBitmapButton(globalVars.app.hMainView.muteBtn, None, wx.Bitmap("./resources/volume.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオンにする"))
	else: setBitmapButton(globalVars.app.hMainView.muteBtn, None, wx.Bitmap("./resources/volume_bk.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオンにする"))

def buttonSetMuteOn():
	if globalVars.app.config.getstring("view","colorMode","white",("white","dark")) == "white":
		setBitmapButton(globalVars.app.hMainView.muteBtn, None, wx.Bitmap("./resources/mute.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオフにする"))
	else: setBitmapButton(globalVars.app.hMainView.muteBtn, None, wx.Bitmap("./resources/mute_bk.dat", wx.BITMAP_TYPE_GIF), _("ミュートをオフにする"))
