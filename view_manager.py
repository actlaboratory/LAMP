import wx
import globalVars

# イベントバインド関数
def listViewSetting(lc):
	lc.AppendColumn("")
	lc.SetDropTarget(fileDrop(lc))

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