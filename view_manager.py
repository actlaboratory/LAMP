import wx
import globalVars
import context_menus

# イベントバインド関数
def listViewSetting(lc):
	lc.AppendColumn("")
	lc.SetDropTarget(fileDrop(lc))
	lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, globalVars.eventProcess.listSelection)
	lc.Bind(wx.EVT_LIST_KEY_DOWN, globalVars.eventProcess.listViewKeyEvent)
	lc.Bind(wx.EVT_CONTEXT_MENU, context_menus.contextMenuOnListView)

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