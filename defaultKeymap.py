# -*- coding: utf-8 -*-
#default key map
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

defaultKeymap={}

defaultKeymap["mainView"]={
	# ファイルメニュー
	"FILE_OPEN": "ctrl+shift+F",
	"DIR_OPEN": "ctrl+shift+O",
	"URL_OPEN": "ctrl+U",
	"M3U_OPEN": "ctrl+O",
	"NEW_M3U8_SAVE": "ctrl+shift+S",
	"M3U8_SAVE": "ctrl+S",
	"M3U_ADD": "ctrl+shift+L",
	"M3U_CLOSE": "ctrl+shift+C",
	"EXIT": "ctrl+Q",
	# 機能メニュー
	"SET_SLEEPTIMER": "ctrl+shift+T",
	"SET_EFFECTOR": "ctrl+E",
	"ABOUT_PLAYING": "ctrl+shift+I",
	# 操作メニュー
	"VOLUME_UP": "ctrl+uparrow",
	"VOLUME_DOWN": "ctrl+downarrow",
	"VOLUME_DEFAULT": "ctrl+shift+uparrow",
	"MUTE": "ctrl+shift+downarrow",
	"PLAY_PAUSE": "ctrl+P/space",
	"STOP": "ctrl+Space",
	"NEXT_TRACK": "ctrl+F",
	"PREVIOUS_TRACK": "ctrl+B",
	"FAST_FORWARD": "ctrl+rightarrow",
	"REWIND": "ctrl+leftarrow",
	"SAY_TIME": "ctrl+T",
	"SKIP": "alt+leftarrow",
	"REVERSE_SKIP": "alt+rightarrow",
	"SKIP_INTERVAL_INCREASE": "alt+uparrow",
	"SKIP_INTERVAL_DECREASE": "alt+downarrow",
	"REPEAT_LOOP": "ctrl+L",
	"SHUFFLE": "ctrl+H",
	"MANUAL_SONG_FEED": "ctrl+shift+H",
	"EXAMPLE": "ctrl+F12/shift+delete/ctrl+c/INSERT/ctrl+BACK",
}

defaultKeymap["playlist"]={
	"POPUP_ADD_QUEUE_HEAD": "ctrl+shift+return",
	"POPUP_ADD_QUEUE": "shift+return",
	"POPUP_COPY": "ctrl+C",
	"POPUP_PASTE": "ctrl+V",
	"POPUP_DELETE": "delete",
	"POPUP_SELECT_ALL": "ctrl+A"
}

defaultKeymap["queue"]={
	"POPUP_ADD_PLAYLIST": "shift+return",
	"POPUP_COPY": "ctrl+C",
	"POPUP_PASTE": "ctrl+v",
	"POPUP_DELETE": "delete",
	"POPUP_SELECT_ALL": "ctrl+A"
}
defaultKeymap["HOTKEY"]={
}