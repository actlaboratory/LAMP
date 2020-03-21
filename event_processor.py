import sys, platform, wx
import winsound

def is64Bit():
	return sys.maxsize > 2 ** 32

#使用環境に応じて適切なdllをロード
if is64Bit():
	from pybass64 import pybass
	from pybass64 import bass_fx
else:
	from pybass import pybass
	from pybass import bass_fx


class eventProcessor():
	def __init__(self):
		self.stopFlag = 0


	def freeBass(self):
		# bass.dllをフリー
		pybass.BASS_Free()

	def refreshView(self):
		# ボタン表示更新
		if self.stopFlag ==1 or self.globalVars.play.handle == 0:
			self.globalVars.frame.playButton.SetLabel("再生")
		elif self.globalVars.play.getChannelState() == pybass.BASS_ACTIVE_PLAYING:
			self.globalVars.frame.playButton.SetLabel("一時停止")
		else:
			self.globalVars.frame.playButton.SetLabel("再生")

		# リスト幅更新
		self.globalVars.frame.playListView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
		self.globalVars.frame.queueView.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)


	def fileChange(self):
		# ストリームがないか停止状態であれば次のファイルを再生
		if self.globalVars.play.handle == 0 or self.globalVars.play.getChannelState() == pybass.BASS_ACTIVE_STOPPED:
			self.nextFile()

	def previousFile(self):
		if self.stopFlag == 1:
			return None
		# プレイリスト再生中であれば
		get = self.globalVars.playlist.getFile()
		if get == self.globalVars.play.fileName:
			# プレイリストの1曲前を再生
			get = self.globalVars.playlist.getPrevious()
			if get != None:
				self.globalVars.play.inputFile(get)
		elif get != None:
			# キューなどからの復帰
			self.globalVars.play.inputFile(get)

	def playButtonControl(self):
		# 再生中は一時停止を実行
		if self.globalVars.play.getChannelState() == pybass.BASS_ACTIVE_PLAYING:
			self.globalVars.play.pauseChannel()
		# 停止中であればファイルを再生
		elif self.stopFlag == 1:
			self.stopFlag = 0
			self.nextFile()
		else:
			self.globalVars.play.channelPlay()

	def nextFile(self):
		# ユーザ操作による停止ではないか
		if self.stopFlag == 1:
			return None
		# キューを確認
		get = self.globalVars.queue.getNext()
		if get == None:
			# キューが空の時はプレイリストを確認
			get = self.globalVars.playlist.getNext()
			if get != None:
				self.globalVars.play.inputFile(get)

		else:
			self.globalVars.play.inputFile(get)

	def stop(self):
		self.stopFlag = 1
		self.globalVars.play.channelFree()
		self.globalVars.playlist.positionReset()
