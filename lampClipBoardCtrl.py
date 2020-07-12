import clipboard

def paste(type):
    """typeにリストオブジェクトを受け取る。"""
    # clipBoardモジュールを使って貼り付けるファイルリストを取得
    c = clipboard.ClipboardFile()
    pasteList = c.GetFileList()
    # ファイルの追加
    type.addFiles(pasteList)
    return
