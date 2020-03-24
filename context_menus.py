import wx
import globalVars

# ポップアップメニュー作成（項目リスト, 無効インデックスリスト）
def makeMenu(val, disableId):
	rtn = wx.Menu()
	idCount = 0
	for s in val:
		item = wx.MenuItem(rtn, idCount, s)
		rtn.Append(item)
		if idCount in disableId:
			rtn.Enable(idCount, False)
		idCount += 1
	return rtn

def contextMenuOnListView(evt):
	values = []
	disable = []
	evtObj = evt.GetEventObject()
	# リストからメニュー作成
	if evtObj == globalVars.app.hMainView.playlistView:
		if evtObj.GetSelectedItemCount() == 0:
			values = [_("貼り付け")]
		else:
			values = [_("再生"), _("キューに追加"), _("キューの先頭に割り込み"), _("コピー"), _("貼り付け"), _("削除"), _("このファイルについて")]
	elif evtObj == globalVars.app.hMainView.queueView:
		if evtObj.GetSelectedItemCount() == 0:
			values = [_("貼り付け")]
		else:
			values = [_("再生"), _("プレイリストに追加"), _("コピー"), _("貼り付け"), _("削除"), _("このファイルについて")]
	# 無効な選択
	if evtObj.GetSelectedItemCount() > 1:
		disable.append(values.index(_("再生")))
		disable.append(values.index(_("このファイルについて")))
	menu = makeMenu(values, disable)
	globalVars.app.hMainView.hFrame.PopupMenu(menu)
