import wx
import globalVars
import context_menus
import defaultKeymap
import keymap

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
		if self.window == globalVars.app.hMainView.playlistView:
			globalVars.playlist.addFiles(files)
		elif self.window == globalVars.app.hMainView.queueView:
			globalVars.queue.addFiles(files)
		return True