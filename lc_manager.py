import wx

def getListCtrlItems(lc):
	rtn = []
	itm = -1
	while True:
		# リストを生成
		itm = lc.GetNextItem(itm, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
		if itm == -1:
			break
		else:
			rtn.append(lc.GetItemText(itm))
	return rtn

def getListCtrlSelections(lc):
	rtn = []
	itm = -1
	while True:
		# リストを生成
		itm = lc.GetNextItem(itm, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if itm == -1:
			break
		else:
			rtn.append(itm)
	return rtn

def setListCtrlSelections(lc, iLst):
	for i in iLst:
		lc.Select(i)
