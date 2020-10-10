import listManager
from views import viewObject

class playlist(viewObject.virtualListCtrl):
    def __init__(self, *pArg, **kArg):
        super().__init__(*pArg, **kArg)
        self.pointer = -1

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
        return self.get()

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

class queue(viewObject.virtualListCtrl):
    def __init__(self, *pArg, **kArg):
        super().__init__(*pArg, **kArg)
        self.pointer = -1

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
        self.lst[index]
        self.pointer = index
