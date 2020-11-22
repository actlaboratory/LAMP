# -*- coding: utf-8 -*-
#Falcon key map management
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import browsableObjects
import keymapHandlerBase
import tabs

class KeymapHandler(keymapHandlerBase.KeymapHandlerBase):

	def __init__(self, dict=None, filter=None):
		super().__init__(dict, filter, permitConfrict=permitConfrict)


#複数メニューに対するキーの割り当ての重複を許すか否かを調べる
#itemsには調べたいAcceleratorEntryのリストを入れる
def permitConfrict(items,log):
	typeCondition=tabs.base.FalconTabBase.selectItemTypeMenuConditions
	countCondition=tabs.base.selectItemMenuConditions;
	flg=0
	for i in [j.refName for j in items]:
		iFlag=0
		#ファイルリストタブ
		if i not in tabs.fileList.FileListTab.blockMenuList:
			if i not in typeCondition[browsableObjects.File]:
				iFlag+=1
			if i not in typeCondition[browsableObjects.Folder]:
				iFlag+=2
			if i not in countCondition[0]:
				iFlag+=4

		#ストリームリストタブ
		if i not in tabs.streamList.StreamListTab.blockMenuList:
			iFlag+=8

		#ドライブリストタブ
		if i not in tabs.driveList.DriveListTab.blockMenuList:
			if i not in tabs.base.FalconTabBase.selectItemTypeMenuConditions[browsableObjects.Drive]:
				iFlag+=16
			if i not in tabs.base.FalconTabBase.selectItemTypeMenuConditions[browsableObjects.NetworkResource]:
				iFlag+=32
			if i not in countCondition[0]:
				iFlag+=64

		#GrepResultTab
		if i not in tabs.grepResult.GrepResultTab.blockMenuList:
			iFlag+=128

		#SearchResultTab
		if i not in tabs.searchResult.SearchResultTab.blockMenuList:
			if i not in typeCondition[browsableObjects.SearchedFile]:
				iFlag+=256
			if i not in typeCondition[browsableObjects.SearchedFolder]:
				iFlag+=512
			if i not in countCondition[0]:
				iFlag+=1024

		if iFlag&flg==0:
			flg+=iFlag
		else:
			#重複によるエラー
			log.warn("key confricted. "+i+" is confrict in "+str(items))
			return False
	log.debug("key not confricted. "+i+" is not confrict in "+str(items))
	return True


class KeyFilter(keymapHandlerBase.KeyFilterBase):
	pass

