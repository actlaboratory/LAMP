import clipboard, listManager

def paste(type):
    """typeにリストオブジェクトを受け取る。"""
    # clipBoardモジュールを使って貼り付けるファイルリストを取得
    c = clipboard.ClipboardFile()
    pasteList = c.GetFileList()
    # ファイルの追加
    listManager.addItems(pasteList, type)
    return

def copy(fileList):
    c = clipboard.ClipboardFile()
    # ファイルの追加
    c.SetFileList(fileList)
    c.SendToClipboard()
    return
