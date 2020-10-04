# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 20XX anonimous <anonimous@sample.com>

import wx

# 言語
SUPPORTING_LANGUAGE={"ja_JP": "日本語","en_US": "English"}

#各種ファイル名
LOG_PREFIX="LAMP"
LOG_FILE_NAME="lamp.log"
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"

#アプリケーション基本情報
APP_NAME="Test Application"
APP_VERSION="0.01"
APP_COPYRIGHT_YEAR="20XX"
APP_DEVELOPERS="Ananimous"

#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED

# メニュー
PLAYLIST_HISTORY= 10500
DEVICE_LIST_MENU = 10000

# パイプとミューテックスオブジェクトの名前
PIPE_NAME = "lamp_pipe_jp0000actlab"

# アイテムタプルのインデックス
ITEM_PATH = 0
ITEM_NAME = 1
ITEM_NUMBER = 2
ITEM_SIZE = 3
ITEM_TITLE = 4
ITEM_LENGTH = 5
ITEM_ARTIST = 6
ITEM_ALBUM = 7
ITEM_ALBUMARTIST = 8

# リスト
PLAYLIST = 101
QUEUE = 102
NOLIST = 103
