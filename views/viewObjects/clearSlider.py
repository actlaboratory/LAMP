# ClearSlider
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import wx
import views.viewObjectBase.sliderBase

def unsupported(*pArg, **kArg):
	raise NotImplementedError("ClearSlider is not support this function.")

class clearSlider(views.viewObjectBase.sliderBase.slider):
	"""
		見やすいスライダ。
		Sliderの派生だが、メモリ表示をサポートしていないので注意すること。
	"""

	# 上下左右の枠の太さ(上＋下、左＋右の２本分の値を偶数で指定)
	BORDER_WIDTH = 6

	def __init__(self, *pArg, **kArg):
		#非対応のスタイルの設定はエラーにする
		style = 0
		if "style" in kArg:
			style = kArg["style"]
		elif len(pArg)>=8:
			style = pArg[7]
		if style!=0:
			if ((style & wx.SL_VERTICAL == wx.SL_VERTICAL) or (style & wx.SL_AUTOTICKS == wx.SL_AUTOTICKS) 
					or (style & wx.SL_MIN_MAX_LABELS == wx.SL_MIN_MAX_LABELS) or (style & wx.SL_VALUE_LABEL == wx.SL_VALUE_LABEL) 
					or (style & wx.SL_LEFT == wx.SL_LEFT) or (style & wx.SL_RIGHT == wx.SL_RIGHT) 
					or (style & wx.SL_TOP == wx.SL_TOP) or (style & wx.SL_BOTTOM == wx.SL_BOTTOM) 
					or (style & wx.SL_BOTH == wx.SL_BOTH) or (style & wx.SL_SELRANGE == wx.SL_SELRANGE)):
				raise ValueError("ClearSlider is not support tick, label, and Lange style.")

		super().__init__(*pArg, **kArg)
		self.Bind(wx.EVT_PAINT, self.paintEvent)
		self.Bind(wx.EVT_SLIDER, self.sliderEvent)
		self.SetThumbLength(50)

	def paintEvent(self,event):
		dc = wx.PaintDC(self)
		self.ELLIPSE_WIDTH = dc.GetSize().GetHeight() / 2

		# はみ出た円を消すために背景色で塗る
		dc.SetPen(wx.Pen(self.GetBackgroundColour(), self.BORDER_WIDTH, wx.PENSTYLE_SOLID))
		dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))
		dc.DrawRectangle(0, 0, dc.GetSize().GetWidth(), dc.GetSize().GetHeight())

		# 枠描画のため背景色で塗る
		dc.SetPen(wx.Pen(wx.Colour(0, 0, 255), self.BORDER_WIDTH, wx.PENSTYLE_SOLID))
		dc.DrawRectangle(self.getLeftMargin() + self.ELLIPSE_WIDTH / 2, 0, dc.GetSize().GetWidth() - self.getLeftMargin() - self.getRightMargin() - self.ELLIPSE_WIDTH, dc.GetSize().GetHeight())

		# 現在のパーセンテージまで塗る
		dc.SetBrush(wx.Brush(wx.Colour(0, 102, 204), wx.BRUSHSTYLE_SOLID))
		dc.SetPen(wx.Pen(wx.Colour(0, 102, 204), 1, wx.PENSTYLE_SOLID))
		dc.DrawRectangle(self.getLeftMargin() + self.BORDER_WIDTH / 2 - 1 + self.ELLIPSE_WIDTH / 2, 0, self.GetValueBarLength(), dc.GetSize().GetHeight())

		# 現在の位置に円を描画
		dc.SetBrush(wx.Brush(wx.Colour(255, 100, 0), wx.BRUSHSTYLE_SOLID))
		dc.SetPen(wx.Pen(wx.Colour(255, 100, 0), 1, wx.PENSTYLE_SOLID))
		dc.DrawEllipse(self.getLeftMargin() + self.BORDER_WIDTH / 2 - 1 + self.GetValueBarLength(), 0, self.ELLIPSE_WIDTH, dc.GetSize().GetHeight())

	# スタートから塗る長さを返す
	# スライダーが最小値の時0、最大値の時にウィンドウ幅-左右マージンとなる
	def GetValueBarLength(self):
		# 0除算対策
		if self.GetMax() - self.GetMin() == 0:
			return 0

		#まずは対象領域の幅を計算
		w = self.GetSize().GetWidth() - self.BORDER_WIDTH - self.getLeftMargin() - self.getRightMargin() - self.ELLIPSE_WIDTH

		#Value 1あたりの幅を計算
		v = w / (self.GetMax() - self.GetMin())

		return v * (self.GetValue() - self.GetMin())

	def getLeftMargin(self):
		return self.GetThumbLength() / 5 + 1

	def getRightMargin(self):
		return self.GetThumbLength() / 5

	def sliderEvent(self,event):
		self.Refresh()

	#描画の関係でサポートできない関数の呼び出しを例外にする
	GetTickFreq = unsupported
	SetTickFreq = unsupported
	SetTick = unsupported
	GetSelEnd = unsupported
	SetSelEnd = unsupported
	GetRange = unsupported
	SetSelection = unsupported
