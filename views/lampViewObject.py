import wx
import globalVars, listManager, menuItemsStore, lampClipBoardCtrl
from views.base import BaseMenu, BaseEvents
from views.viewObjectBase import virtualListCtrlBase

class playlist(virtualListCtrlBase.virtualListCtrl):
    def __init__(self, *pArg, **kArg):
        super().__init__(*pArg, **kArg)
        self.identifier = "playlist"
        self.pointer = -1
        # イベント処理系
        events = Events(self, self.identifier)
        self.menu=Menu(self.identifier)
        self.menu.Apply(self, self.identifier)
        self.Bind(wx.EVT_MENU, events.OnMenuSelect)
        self.SetAcceleratorTable(self.menu.acceleratorTable)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)

    def OnGetItemText(self, item, column):
        if column == 0: column = 1
        return super().OnGetItemText(item, column)

    def get(self):
        if self.pointer >= 0 and self.pointer < len(self.lst):
            return self.lst[self.pointer]
        elif self.pointer == -1 and len(self.lst) > 0:
            self.pointer = 0
            return self.lst[self.pointer]
        else:
            return None

    def getPrevious(self):
        if self.pointer >= 0: self.pointer -= 1
        if self.pointer >= 0: return self.get()
        else: return None

    def getNext(self):
        if self.pointer < len(self.lst) - 1: self.pointer += 1
        else: return None
        return self.get()

    def getPointer(self):
        return self.pointer

    def setPointer(self, index):
        if index == -1: self.pointer = -1
        else:
            self.lst[index]
            self.pointer = index
    
    def setList(self, lst):
        super().setList(lst)
        self.pointer = -1

    def clear(self):
        self.SetItemCount(0)
        super().clear()
        self.pointer = -1

    def insert(self, index, object):
        t = self.get()
        super().insert(index, object)
        if t != None: self.pointer[self.lst.index(t)]
        
    def pop(self, index):
        t = self.get()
        ret = super().pop(index)
        if t in self.lst: self.pointer = self.lst.index(t)
        else: self.pointer = -1
        return ret

    def remove(self, object):
        t = self.get()
        super().remove(object)
        if t in self.lst: self.pointer = self.lst.index(t)
        else: self.pointer = -1

    def reverse(self):
        super().reverse()
        self.pointer = -1

    def sort(self):
        super().sort()
        self.pointer = -1

    def __delitem__(self, key):
        t = self.get()
        super().__delitem__(key)
        if t in self.lst: self.pointer = self.lst.index(t)
        else: self.pointer = -1

    # to do 演算シミュレータを実装

    def onContextMenu(self, evt):
        self.menu.Apply(self, self.identifier)
        evt.GetEventObject().PopupMenu(self.menu.hPopupMenu, evt)

class queue(virtualListCtrlBase.virtualListCtrl):
    def __init__(self, *pArg, **kArg):
        super().__init__(*pArg, **kArg)
        self.identifier = "queue"
        self.pointer = -1
        # イベント処理系
        events = Events(self, self.identifier)
        self.menu=Menu(self.identifier)
        self.menu.Apply(self, self.identifier)
        self.Bind(wx.EVT_MENU, events.OnMenuSelect)
        self.SetAcceleratorTable(self.menu.acceleratorTable)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)

    def OnGetItemText(self, item, column):
        if column == 0: column = 1
        return super().OnGetItemText(item, column)

    def get(self):
        if self.pointer >= 0 and self.pointer < len(self.lst):
            return self.lst[self.pointer]
        elif self.pointer == -1 and len(self.lst) > 0:
            self.pointer = 0
            return self.lst[self.pointer]
        else: return None

    def getPointer(self):
        return self.pointer

    def setPointer(self, index):
        if index != -1: self.lst[index] #リセットは可能
        self.pointer = index

    def onContextMenu(self, evt):
        self.menu.Apply(self, self.identifier)
        evt.GetEventObject().PopupMenu(self.menu.hPopupMenu)

class Menu(BaseMenu):
    def Apply(self,target, identifier):
        """指定されたウィンドウに、メニューを適用する。"""

        #メニューの大項目を作る
        self.hPopupMenu=wx.Menu()

        #ポップアップメニューの中身
        self.RegisterMenuCommand(self.hPopupMenu,"POPUP_PLAY",_("再生"))
        if target.GetSelectedItemCount() != 1:
            self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_PLAY"), False)
        if identifier == "playlist":
            self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE_HEAD",_("キューの先頭に割り込み"))
            self.RegisterMenuCommand(self.hPopupMenu,"POPUP_ADD_QUEUE",_("キューに追加"))
            if target.GetSelectedItemCount() == 0:
                self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE_HEAD"), False)
                self.hPopupMenu.Enable(menuItemsStore.getRef("POPUP_ADD_QUEUE"), False)
        if identifier == "queue":
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
                t = []
                for i in self.parent.getItemSelections(): t.append(self.parent[i][0])
                listManager.addItems(t, globalVars.app.hMainView.queueView, 0)
        elif selected==menuItemsStore.getRef("POPUP_ADD_QUEUE"):
            if self.parent.GetSelectedItemCount() != 0:
                t = []
                for i in self.parent.getItemSelections(): t.append(self.parent[i][0])
                listManager.addItems(t, globalVars.app.hMainView.queueView)
        elif selected==menuItemsStore.getRef("POPUP_ADD_PLAYLIST"):
            if self.parent.GetSelectedItemCount() != 0:
                t = []
                for i in self.parent.getItemSelections(): t.append(self.parent[i][0])
                listManager.addItems(t, globalVars.app.hMainView.playlistView)
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
