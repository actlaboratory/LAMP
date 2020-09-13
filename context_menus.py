import wx
import globalVars
import globalVars
import menuItemsStore
import lc_manager
import data_dict
import lampClipBoardCtrl
from views.base import BaseMenu, BaseEvents
from views import objectDetail

def setContextMenu(listCtrl, identifire):
    events = Events(listCtrl, "listView")
    menu=Menu("mainView")
    menu.Apply(listCtrl, identifire)
    listCtrl.Bind(wx.EVT_MENU, events.OnMenuSelect)
    return menu

def contextMenuOnListView(evt):
    if evt.GetEventObject() == globalVars.app.hMainView.playlistView:
        identifire = "playlist"
    elif evt.GetEventObject() == globalVars.app.hMainView.queueView:
        identifire = "queue"
    globalVars.popupMenu4listView.Apply(evt.GetEventObject(), identifire)
    evt.GetEventObject().PopupMenu(globalVars.popupMenu4listView.hPopupMenu)

class Menu(BaseMenu):
    def Apply(self,target, identifire):
        """指定されたウィンドウに、メニューを適用する。"""

        #メニューの大項目を作る
        self.hPopupMenu=wx.Menu()

        #ポップアップメニューの中身
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_PLAY",_("再生"))
        if target.GetSelectedItemCount() != 1:
            self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_PLAY"), False)
        if identifire == "playlist":
            self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE_HEAD",_("キューの先頭に割り込み"))
            self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE",_("キューに追加"))
            if target.GetSelectedItemCount() == 0:
                self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"), False)
                self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE"), False)
        if identifire == "queue":
            self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_PLAYLIST",_("プレイリストに追加"))
            if target.GetSelectedItemCount() == 0:
                self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_PLAYLIST"), False)
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_COPY",_("コピー"))
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_PASTE",_("貼り付け"))
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_DELETE",_("削除"))
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_SELECT_ALL",_("すべてを選択"))
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ABOUT",_("このファイルについて"))
        if target.GetSelectedItemCount() == 0:
            self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_COPY"), False)
            self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_DELETE"), False)
            self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ABOUT"), False)


class Events(BaseEvents):
    def OnMenuSelect(self,event):
        """メニュー項目が選択されたときのイベントハンドら。"""
        selected=event.GetId()#メニュー識別しの数値が出る

        if selected==menuItemsStore.getRef("POPUP_PLAY"):
            globalVars.eventProcess.listSelection(self.parent)
        elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"):
            ls = lc_manager.getListCtrlPaths(self.parent)
            globalVars.queue.addFiles(ls, 0)
        elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE"):
            ls = lc_manager.getListCtrlPaths(self.parent)
            globalVars.queue.addFiles(ls)
        elif selected==menuItemsStore.getRef("POPUP_ADD_PLAYLIST"):
            ls = lc_manager.getListCtrlPaths(self.parent)
            globalVars.playlist.addFiles(ls)
        elif selected==menuItemsStore.getRef("POPUP_COPY"):
            fList = lc_manager.getListCtrlPaths(self.parent)
            lampClipBoardCtrl.copy(fList)
        elif selected==menuItemsStore.getRef("POPUP_PASTE"):
            lampClipBoardCtrl.paste(lc_manager.getList(self.parent))
        elif selected==menuItemsStore.getRef("POPUP_DELETE"):
            lst = lc_manager.getList(self.parent)
            index = lc_manager.getListCtrlSelections(self.parent)
            cnt = 0
            for i in index:
                i = i-cnt
                globalVars.eventProcess.delete(lst,i)
                cnt += 1
        elif selected==menuItemsStore.getRef("POPUP_SELECT_ALL"):
            for i in range(self.parent.GetItemCount()):
                self.parent.Select(i - 1)
        elif selected==menuItemsStore.getRef("POPUP_ABOUT"):
            item = self.parent.GetItemData(lc_manager.getListCtrlSelections(self.parent)[0])
            globalVars.dataDict.getTags([item])
            data_dict.infoDialog(item)            
