# -*- coding: utf-8 -*-
#Falcon clipboard utility
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import struct
import clipboardHelper

COPY=1
MOVE=2

class ClipboardFile(object):
	def __init__(self):
		self.lst=None
		self.operation=COPY
		self.bytes=0

	def SetFileList(self,lst):
		self.byte=bytearray(struct.pack('iiiii', 20, 0, 0, 0, 1))
		for elem in lst:
			a=bytearray(elem.encode('UTF-16'))
			a.append(0)
			a.append(0)
			del(a[0:2])
			self.byte+=a
		#end for
		self.byte.append(0)
		self.byte.append(0)

	def SetOperation(self,op):
		self.operation=op

	def GetFileList(self):
		with clipboardHelper.Clipboard() as c:
			lst=c.get_dropped_files()
		#end
		return lst

	def GetOperation(self):
		with clipboardHelper.Clipboard() as c:
			fmt=c.register_format("Preferred DropEffect")
			buf=c.get_data(fmt)
			op=struct.unpack('i',buf)[0]
		#end with
		return op
	#end getOperation

	def SendToClipboard(self):
		with clipboardHelper.Clipboard() as c:
			c.empty()
			c.set_data(clipboardHelper.ClipboardFormats.drop_handle,bytes(self.byte))
			fmt=c.register_format("Preferred DropEffect")
			c.set_data(fmt,struct.pack('i', self.operation))
		#end with
	#end def

	def ReceiveFromClipboard(self):
		with clipboardHelper.Clipboard() as c:
			s=c.get_dropped_files()
		#end with
