import wx

class virtualListCtrl(wx.ListCtrl):
    # listの機能を組み込み
    def __init__(self, *pArg, **kArg):
        lPArg = list(pArg)
        if len(lPArg) >= 5: lPArg[4] = lPArg[4] | wx.LC_REPORT | wx.LC_VIRTUAL
        elif "style" in kArg: kArg["style"] = kArg["style"] | wx.LC_REPORT | wx.LC_VIRTUAL
        else: kArg["style"] = wx.LC_REPORT | wx.LC_VIRTUAL
        self.lst = []
        super().__init__(*lPArg, **kArg)

    def getList(self):
        return self.copy()
    
    def setList(self, lst):
        lstLen = len(lst)
        self.lst = []
        super().SetItemCount(lstLen)
        if lstLen > 0: super().RefreshItems(0, lstLen)


    #
    # ビュー部分
    # 
    def OnGetItemText(self, item, column):
        obj = self.lst[item]
        if hasattr(obj, '__iter__'): return str(obj[column]) # イテレーション可能なオブジェクト
        else: return obj.getListTuple()[column] # getListTupleを実装するオブジェクト




    #
    # リスト部分
    #
    def append(self, object):
        self.lst.append(object)
        super().SetItemCount(len(self.lst))
        super().RefreshItem(len(self.lst)-1)

    def clear(self):
        self.lst.clear()
        super().SetItemCount(0)

    def copy(self):
        return self.lst.copy()

    def count(self, value):
        return self.lst.count(value)

    def extend(self, iterable):
            self.lst.extend(iterable)
            newLen = len(self.lst)
            super().SetItemCount(newLen)
            if len(iterable) > 0: super().RefreshItems(newLen-len(iterable), newLen-1)

    def index(self, *pArg, **kArg):
        return self.lst.index(*pArg, *kArg)

    def insert(self, index, object):
        self.lst.insert(index, object)
        super().RefreshItems(index, len(self.lst)-1)

    def pop(self, index):
        ret = self.lst.pop(index)
        super().RefreshItems(index, len(self.lst)-1)
        return ret

    def remove(self, value):
        index = self.lst.index(value)
        self.lst.remove(value)
        super().RefreshItems(index, len(self.lst)-1)

    def reverse(self):
        self.lst.reverse()
        super().RefreshItems(0, len(self.lst)-1)

    def sort(self):
        self.lst.sort()
        super().RefreshItems(0, len(self.lst)-1)

    
    # 拡張比較
    def __lt__(self, other):
        return self.lst.__lt__(other)

    def __le__(self, other):
        return self.lst.__le__(other)

    def __eq__(self, other):
        return self.lst.__eq__(other)

    def __ne__(self, other):
        return self.lst.__ne__(other)

    def __gt__(self, other):
        return self.lst.__gt__(other)

    def __ge__(self, other):
        return self.lst.__ge__(other)

    
    def __hash__(self):
        return self.lst.__hash__()


    # to do
    # def __init_subclass(cls):


    # 
    def __len__(self):
        return self.lst.__len__()

    def __mul__(self, other):
        return self.lst.__mul__(other)

    def __getitem__(self, key):
        return self.lst.__getitem__(key)

    def __setitem__(self, key, value):
        self.lst.__setitem__(key, value)
        super().RefreshItem(key)

    def __delitem__(self, key):
        self.lst.__delitem__(key)
        super().RefreshItems(key, len(self.lst)-1)

    def __iter__(self):
        return self.lst.__iter__()

    def __reversed__(self):
        return self.lst.__reversed__()
    
    def __contains__(self, item):
        return self.lst.__contains__(item)


    # 数値型エミュレート
    def __add__(self, value):
        return self.lst.__add__(value)

    def __rmul__(self, other):
        return self.lst.__rmul__(other)

    def __iadd__(self, other):
        oldLen = len(self.lst)
        self.lst.__iadd__(other)
        newLen = len(self.lst)
        super().SetItemCount(len(newLen))
        if oldLen < newLen: super().RefreshItems(oldLen, newLen-1)
        
    def __imul__(self, other):
        oldLen = len(self.lst)
        self.lst.__imul__(other)
        newLen = len(self.lst)
        super().SetItemCount(newLen)
        if oldLen < newLen: super().RefreshItems(oldLen, newLen-1)
        elif newLen == 0: super().SetItemCount(0)
