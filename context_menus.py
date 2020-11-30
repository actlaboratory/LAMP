import wx
import globalVars
import globalVars
import listManager
import menuItemsStore
import lampClipBoardCtrl
from views.base import BaseMenu, BaseEvents
from views import objectDetail

def setContextMenu(listCtrl, identifier):
    events = Events(listCtrl, "listView")
    menu=Menu(identifier)
    menu.Apply(listCtrl, identifier)
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
            if self.parent.GetSelectedItemCount() == 1:
                globalVars.eventProcess.listSelection(self.parent)
        elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"):
            if self.parent.GetSelectedItemCount() != 0:
                t = self.parent[self.parent.GetFirstSelected()]
                listManager.addItems((t[0],), globalVars.app.hMainView.queueView, 0)
        elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE"):
            if self.parent.GetSelectedItemCount() != 0:
                t = self.parent[self.parent.GetFirstSelected()]
                listManager.addItems((t[0],), globalVars.app.hMainView.queueView)
        elif selected==menuItemsStore.getRef("POPUP_ADD_PLAYLIST"):
            if self.parent.GetSelectedItemCount() != 0:
                t = self.parent[self.parent.GetFirstSelected()]
                listManager.addItems((t[0],), globalVars.app.hMainView.playlistView)
        elif selected==menuItemsStore.getRef("POPUP_COPY"):
            if self.parent.GetSelectedItemCount() != 0:
                fList = []
                i = self.parent.GetFirstSelected()
                if i >= 0:
                    fList.append(self.parent[i][0])
                    while True:
                        i = self.parent.GetNextSelected(i)
                        if i >= 0: fList.append(self.parent[i][0])
                        else: break
                lampClipBoardCtrl.copy(fList)
        elif selected==menuItemsStore.getRef("POPUP_PASTE"):
            lampClipBoardCtrl.paste(self.parent)
        elif selected==menuItemsStore.getRef("POPUP_DELETE"):
            if self.parent.GetSelectedItemCount() != 0:
                globalVars.eventProcess.delete(self.parent)
        elif selected==menuItemsStore.getRef("POPUP_SELECT_ALL"):
            for i in range(self.parent.GetItemCount()):
                self.parent.Select(i - 1)
        elif selected==menuItemsStore.getRef("POPUP_ABOUT"):
            if self.parent.GetSelectedItemCount() == 1:
                index = self.parent.GetFirstSelected()
                t = self.parent[index]
                tag = listManager.getTags([t])
                self.parent[index] = tag[0]
                t = self.parent[index]
                listManager.infoDialog(t)
