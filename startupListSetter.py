# startupPlaylistSetter
#Copyright (C) 2021 Hiroki Fujii <hfujii@hisystron.com>

import os
import globalVars, fxManager
from views import mkDialog

def run():
    f = globalVars.listInfo.playlistFile
    if f != None and os.path.exists(f):
        globalVars.app.config["player"]["startupPlaylist"] = f
        d = mkDialog.Dialog("set startup playlist ok")
        d.Initialize(_("設定完了"), _("起動時に開くプレイリストに設定しました。\n%s") %(f,), ("OK",), sound=False)
        fxManager.confirm()
        d.Show()
    else:
        d = mkDialog.Dialog("set startup playlist error")
        d.Initialize(_("エラー"), _("設定に失敗しました。"), ("OK",), sound=False)
        fxManager.error()
        d.Show()