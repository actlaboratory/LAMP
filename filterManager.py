# -*- coding: utf-8 -*-
# LAMP filter Manager
#Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import logging
import os

import constants
import globalVars
import re


FILTER_FILE_OUT = 0
FILTER_FILE_IN = 1
FILTER_PATH_OUT = 2
FILTER_PATH_IN = 3

filterTypes = {
	FILTER_FILE_OUT:_("ファイル名で除外"),
	FILTER_FILE_IN:_("ファイル名で通過"),
	FILTER_PATH_OUT:_("パスで除外"),
	FILTER_PATH_IN:_("パスで通過")
}


class FilterManager():
	def __init__(self):
		self.log = logging.getLogger("%s.%s" % (constants.LOG_PREFIX,"filterManager"))
		self.config = globalVars.app.config
		self.log.debug("init")
		self.load()

	# 4つの辞書として設定内容を取得
	def getDic(self):
		t = {}
		p = {}
		status = {}
		startup = {}
		for f in self.filters:
			t[f.getName()]=f.getType()
			p[f.getName()]=f.getPattern()
			status[f.getName()]=f.isEnable()
			startup[f.getName()]=f.getStartup()
		return t,p,status,startup

	def get(self,index):
		return self.filters[index]

	def getList(self):
		return self.filters

	def load(self):
		self.log.debug("load from file")
		# ファイルから読込
		types = dict(self.config.items("filter_types"))
		patterns = dict(self.config.items("filter_patterns"))
		startup = dict(self.config.items("filter_startup"))

		r = self._load(types,patterns,startup,startup)

		# 読込中に異常があれば設定ファイルを更新
		if not r:
			self.save()

	# 辞書内容で全てのフィルタを上書き
	def loadDic(self,types,patterns,status,startup):
		self.log.debug("load from dic")
		self._load(types,patterns,status,startup)
		self.save()

	# 4つの辞書から読み込んで設定を上書き
	# 異常があればFalse、なければTrueを返す
	# この関数は保存を行わない
	def _load(self,types,patterns,status,startup):
		self.filters = []			# 結果のFilterオブジェクトを格納
		flg = True					# 異常設定検知フラグ

		# キーの一覧生成
		# 並び順の維持のためsetは使えない
		keys = []
		for k in types.keys():
			if k in patterns.keys() and k in startup.keys():
				keys.append(k)

		if len(keys)!=len(types) or len(keys)!=len(patterns) or len(keys)!=len(startup):
			flg = False

		# filterオブジェクト生成
		for k in keys:
			try:				# 正規表現として不成立な可能性があるため
				t = types[k]
				try:			# iniから読み込むと数値もstrになるので可能な場合は数値として解釈
					if type(t)==str:
						t = int(t)
				except:
					pass		# 設定画面から来た場合など、文字列で指定された場合はそのまあまでよい
				if type(t)==str:
					t = getType(t)
				else:
					if t<0 or t>=len(filterTypes):
						raise ValueError("type %d is out of range" % t)
				ptn = re.compile(patterns[k])
				self.filters.append(Filter(k,t,ptn,toBoolean(status[k]),toBoolean(startup[k])))
			except Exception as e:
				self.log.error(e)
				flg = False
				pass			# 成立しない設定は無視
		self.log.info("%d settings are loaded." % len(self.filters))
		return flg

	def save(self):
		self.config.remove_section("filter_types")
		self.config.remove_section("filter_patterns")
		self.config.remove_section("filter_startup")
		for f in self.filters:
			self.config["filter_types"][f.getName()]=f.getType()
			self.config["filter_patterns"][f.getName()]=f.getPattern()
			self.config["filter_startup"][f.getName()]=f.getStartup()

	# 全ての有効なフィルタに通過すればTrue、そうでなければFalseを返す
	def test(self,path):
		for f in self.filters:
			if f.enable and f.test(path)==False:
				return False
		return True


class Filter():
	def __init__(self,name,t,pattern,enable=False,startup=False):
		assert type(name)==str
		assert type(t)==int
		assert type(pattern)==re.Pattern
		self.name = name
		if t<0 or t>=len(filterTypes):
			raise ValueError("type %d out of range" % t)
		self.t = t
		self.pattern = pattern
		self.enable = enable
		self.startup = startup

	def getName(self):
		return self.name

	def getPattern(self):
		return self.pattern.pattern

	def getType(self):
		return self.t

	def getTypeString(self):
		return getTypeString(self.t)

	def isEnable(self):
		return self.enable

	def setEnable(self,status):
		self.enable = status

	def getStartup(self):
		return self.startup

	# pathを受け取り、通過させるならTrue、除外するならFalseを返す
	def test(self,path):
		path = path.lower()
		if self.t==FILTER_FILE_OUT:
			fn = os.path.basename(path)
			return self.pattern.fullmatch(fn) == None
		elif self.t==FILTER_FILE_IN:
			fn = os.path.basename(path)
			return self.pattern.fullmatch(fn) != None
		elif self.t==FILTER_PATH_OUT:
			return self.pattern.fullmatch(path) == None
		elif self.t==FILTER_PATH_IN:
			return self.pattern.fullmatch(path) != None
		else:
			raise NotImplementedError


# intのtype値tに対応する表示文字列を返す
def getTypeString(t):
	try:
		return filterTypes[t]
	except KeyError as e:
		if type(t)!=int:
			raise TypeError("filter type must be int")
		else:
			raise ValueError("filterType %d is missing." % t)

# typeStringに対応するint型のtype値を返す
def getType(s):
	try:
		return list(filterTypes.values()).index(s)
	except KeyError:
		if type(s)!=str:
			raise TypeError("filter typeString must be str")
		else:
			raise ValueError("filterTypeString %s is missing." % s)

def getTypeStringList():
	return list(filterTypes.values())

# 文字列sの内容を基にboolに変換
# sがboolならそのままにする
def toBoolean(s):
	if type(s)==bool:
		return s
	return s.lower() in ("true","yes","on","1","enable")
