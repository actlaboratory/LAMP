# -*- coding: utf-8 -*-
#constant values
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx

# 言語
SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"

#各種ファイル名
LOG_PREFIX="LAMP"
LOG_FILE_NAME="lamp.log"
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"

#アプリケーション基本情報
APP_NAME="LAMP"
APP_FULL_NAME = "Light and Accessible Music Player"
APP_VERSION="3.0.1"
APP_LAST_RELEASE_DATE = "2021-02-24"
APP_ICON = "icon.ico"
APP_COPYRIGHT_YEAR="2019-2025"
APP_LICENSE="GNU General Public License2.0 or later"
APP_DEVELOPERS="Hiroki Fujii, ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/LAMP"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All rights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

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
FILTER_LIST_MENU = 11000

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

# API定数
API_VERSION = 1
API_DEFAULT_INTERVAL = 2
#API_BASE_URL = "http://localhost:10100/"
API_BASE_URL = "https://lamp.actlab.org/"
API_COMUNICATION_URL = API_BASE_URL + "api/v1/comunication"
API_SOFTWAREMANAGE_URL = API_BASE_URL + "api/v1/softwaremanage"
API_SOFTWAREENTRY_URL = API_BASE_URL + "api/v1/entry"
API_PUTFILE_URL = API_BASE_URL + "api/v1/putfile"

# リスト
PLAYLIST = 101
QUEUE = 102
NOLIST = 103

# ダイアログの選択
DIALOG_PE_CONTINUE = 0 #続行

#build関連定数
BASE_PACKAGE_URL = "https://github.com/actlaboratory/LAMP/releases/download/2.0.0/LAMP-2.0.0.zip"
PACKAGE_CONTAIN_ITEMS = ("fx", "resources")#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "lamp.py"#起動用ファイルを指定

