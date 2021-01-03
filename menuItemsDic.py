#menuItemsDic
#Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)



dic={
	# ファイルメニュー
	"FILE_OPEN": _("ファイルを開く(&O)"),
	"DIR_OPEN": _("フォルダを開く(&F)"),
	"URL_OPEN": _("URLを開く(&U)"),
	"M3U_OPEN": _("プレイリストを開く(&P)"),
	"NEW_M3U8_SAVE": _("名前を付けてプレイリストを保存(&A)"),
	"M3U8_SAVE": _("プレイリストを上書き保存(&S)"),
	"M3U_ADD": _("プレイリストから読み込む(&L)"),
	"M3U_CLOSE": _("プレイリストを閉じる(&C)"),
	"EXIT": _("終了(&X)"),
	
	#機能メニュー
	"SET_SLEEPTIMER": _("スリープタイマーを設定(&S)"),
	"SET_EFFECTOR": _("エフェクター(&F)"),
	"ABOUT_PLAYING": _("再生中のファイルについて(&A)"),
	
	# プレイリストメニュー
	"PLAYLIST_HISTORY_LABEL": _("履歴（20件まで）"),
	
	# 操作メニュー
	"PLAY_PAUSE": _("再生 / 一時停止(&P)"),
	"STOP": _("停止(&S)"),
	"FAST_FORWARD": _("早送り(&F)"),
	"REWIND": _("巻き戻し(&B)"),
	"PREVIOUS_TRACK": _("前へ / 頭出し(&R)"),
	"NEXT_TRACK": _("次へ(&N)"),
	"SKIP": _("スキップ(&K)"),
	"REVERSE_SKIP": _("逆スキップ(&E)"),
	# スキップ間隔設定
	"SET_SKIP_INTERVAL_SUB": _("スキップ間隔設定(&C)"),
	"SKIP_INTERVAL_INCREASE": _("スキップ間隔を大きくする(&I)"),
	"SKIP_INTERVAL_DECREASE": _("スキップ間隔を小さくする(&D)"),
	# 音量
	"SET_VOLUME_SUB": _("音量(&V)"),
	"VOLUME_100": _("音量を10&0%に設定"),
	"VOLUME_UP": _("音量を上げる(&U)"),
	"VOLUME_DOWN": _("音量を下げる(&D)"),
	"MUTE": _("ミュート(&M)"),
	# リピート・ループ
	"SET_REPEAT_LOOP_SUB": _("リピート・ループ(&L)")+"\tCtrl+R",
	"REPEAT_LOOP": _("リピート・ループ切り替え"),
	"REPEAT_LOOP_NONE": _("解除する(&N)"),
	"RL_REPEAT": _("リピート(&R)"),
	"RL_LOOP": _("ループ(&L)"),
	"SHUFFLE": _("シャッフル再生(&H)"),
	"MANUAL_SONG_FEED": _("手動で曲送り(&M)"),

	# 設定メニュー
	"SET_DEVICE_SUB": _("再生出力先の変更(&O)"),
	"SET_STARTUPLIST": _("このプレイリストを起動時に開く"),
	"FILE_ASSOCIATE": _("ファイルの関連付け(&A)"),
	"SET_SENDTO": _("送るメニューに登録(&S)"),
	"SET_KEYMAP": _("ショートカットキー設定(&K)"),
	"SET_HOTKEY": _("グローバルホットキー設定(&G)"),
	"ENVIRONMENT": _("環境設定(&P)"),

	#ヘルプメニューの中身
	"HELP": _("ヘルプ(&H)"),
	"CHECK_UPDATE": _("更新の確認(&U)"),
	"VERSION_INFO": _("バージョン情報(&V)"),
	
	"SAY_TIME": _("経過時間の読み上げ"),

	"":""		#セパレータ追加時用
}
