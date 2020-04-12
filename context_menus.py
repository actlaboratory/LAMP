import wx
import globalVars
import menuItemsStore
from views.base import BaseMenu, BaseEvents

def contextMenuOnListView(evt):
	menu=Menu("mainView")
	events = Events(evt.GetEventObject(), "listView")
	menu.Apply(evt.GetEventObject())
	evt.GetEventObject().PopupMenu(menu.hPopupMenu)
	evt.GetEventObject().Bind(wx.EVT_MENU, events.OnMenuSelect)

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hPopupMenu=wx.Menu()

		#ポップアップメニューの中身
		self.RegisterMenuCommand(self.hPopupMenu,"POPUP_PLAY",_("再生"))
		if target.GetSelectedItemCount() != 1:
			self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_PLAY"), False)
		if target == globalVars.app.hMainView.playlistView:
			self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE_HEAD",_("キューの先頭に割り込み"))
			self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE",_("キューに追加"))
			if target.GetSelectedItemCount() == 0:
				self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"), False)
				self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE"), False)
		if target == globalVars.app.hMainView.queueView:
			self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_PLAYLIST",_("プレイリストに追加"))
			if target.GetSelectedItemCount() == 0:
				self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_PLAYLIST"), False)
		self.RegisterMenuCommand(self.hPopupMenu,"POPUP_COPPY",_("コピー"))
		self.RegisterMenuCommand(self.hPopupMenu,"POPUP_PASTE",_("貼り付け"))
		self.RegisterMenuCommand(self.hPopupMenu,"POPUP_DELETE",_("削除"))
		self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ABOUT",_("このファイルについて"))
		if target.GetSelectedItemCount() == 0:
			self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_COPPY"), False)
			self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_DELETE"), False)
			self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ABOUT"), False)


class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		selected=event.GetId()#メニュー識別しの数値が出る

		if selected==menuItemsStore.getRef("POPUP_PLAY"):
			globalVars.eventProcess.listSelection(self.parent)
		elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"):
			pass
		elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE"):
			pass
		elif selected==menuItemsStore.getRef("POPUP_ADD_PLAYLIST"):
			pass
		elif selected==menuItemsStore.getRef("POPUP_COPPY"):
			pass
		elif selected==menuItemsStore.getRef("POPUP_PASTE"):
			pass
		elif selected==menuItemsStore.getRef("POPUP_ABOUT"):
			pass
		