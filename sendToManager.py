#"SendTo" Manager
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>

import win32com, sys, os
import constants, fxManager
from views import mkDialog

SENDTO_PATH = os.environ["APPDATA"]+"\\Microsoft\\Windows\\SendTo\\"

def sendToCtrl(label):
    sFile = SENDTO_PATH + str(label) + ".lnk"
    if os.path.isfile(sFile):
        d = mkDialog.Dialog("sendToDeleteDialog")
        d.Initialize(_("確認"), _("%sは、送るメニューに登録されています。\n登録を解除しますか。" %constants.APP_NAME), (_("はい")+"(&Y)", _("いいえ")+"(&N)"))
        r = d.Show()
        if r == 1: return
        else:
            try:
                os.remove(sFile)
                _ok(_("送るメニューの登録を解除しました。"))
            except OSError:
                _error(_("登録の解除に失敗しました。"))
    else:
        if _makeSendTo(label): _ok(_("%sを、送るメニューに登録しました。\n実行するには、「%s」を選択します。" %(constants.APP_NAME, label)))
        else: _error(_("登録に失敗しました。"))
            


def _makeSendTo(label):
    if not hasattr(sys,"frozen"): return False
    try:
        shortCut = SENDTO_PATH + str(label) + ".lnk"
        ws = win32com.client.Dispatch("wscript.shell")
        scut=ws.CreateShortcut(shortCut)
        scut.TargetPath=sys.executable
        scut.Save()
        return True
    except OSError as e:
        return False

def _error(message):
    fxManager.error()
    d = mkDialog.Dialog("sendToErrorDialog")
    d.Initialize(_("エラー"), message, ("OK",))
    d.Show()

def _ok(message):
    d = mkDialog.Dialog("sendToSuccessDialog")
    d.Initialize(_("完了"), message, ("OK",))
    d.Show()