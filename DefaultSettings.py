# -*- coding: utf-8 -*-
#default config
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

from ConfigManager import *


class DefaultSettings:
	def get():
		config = ConfigManager()
		config["general"]={
			"language": "ja-JP",
			"fileVersion": "101",
			"locale": "ja-JP",
			"update": True,
			"timeout": 5,
			"log_level": "0",
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":"normal"
		}
		config["speech"]={
			"reader" : "AUTO"
		}
		config["mainView"]={
			"sizeX": "800",
			"sizeY": "600",
		}
		config["player"]={
			"outputDevice": "default",
			"repeatStartup": False,
			"skipInterval": "30",
			"fadeOutOnExit": False,
			"fileInterrupt": "play",
			"playlistInterrupt": "open",
			"manualSongFeed": False,
			"startupPlaylist": ""
		}
		config["volume"]={
			"default": "50",
		}
		config["notification"]={
			"sound": True,
			"errorSound": True,
			"outputDevice": "same",
			"ignoreError": False
		}
		config["network"]={
			"manual_proxy": False,
			"proxy_server": "",
			"proxy_port": 8080,
			"user_name": "",
			"software_key": "",
			"ctrl_client": True
		}
		config["filter_types"]={
		}
		config["filter_patterns"]={
		}
		return config

initialValues={}
"""
	この辞書には、ユーザによるキーの削除が許されるが、初回起動時に組み込んでおきたい設定のデフォルト値を設定する。
	ここでの設定はユーザの環境に設定ファイルがなかった場合のみ適用され、初期値として保存される。
"""
initialValues["filter_types"]={
	"filter off vocal" : "0",
}

initialValues["filter_patterns"]={
	"filter off vocal" : ".*((vocal off)|(off vocal)|(instrumental)|(\(カラオケ\))).*",
}

initialValues["filter_startup"]={
	"filter off vocal" : "False",
}
