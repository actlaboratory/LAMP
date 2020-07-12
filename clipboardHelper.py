# https://qiita.com/katabamisan/items/230221ca0bcada38efde
from ctypes import *
from enum import IntEnum
from array import array
import win32clipboard
import win32api

falconHelper=cdll.LoadLibrary("viewhelper.dll")


class Clipboard(object):
	def open(self):
		OpenClipboard = windll.user32.OpenClipboard
		OpenClipboard.restype = c_bool
		if not OpenClipboard(c_void_p(0)):
			raise WindowsError()
		return

	def close(self):
		CloseClipboard = windll.User32.CloseClipboard
		if not CloseClipboard():
			raise WindowsError()
		return

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		self.close()
		return False

	def get_data_handle(self, format):
		user32 = windll.user32
		GetClipboardData = user32.GetClipboardData
		GetClipboardData.restype = c_void_p
		handle = GetClipboardData(c_uint(format))
		if handle == c_void_p(0) and get_last_error() != 0:
			raise WindowsError()
		return handle

	def get_data_size(self, format):
		kernel32 = windll.kernel32
		handle = self.get_data_handle(format)
		GlobalSize = kernel32.GlobalSize
		GlobalSize.restype = c_uint32
		size = GlobalSize(handle)
		if handle == c_void_p(0) and get_last_error() != 0:
			raise WindowsError()
		return size.raw

	def get_data(self, format):
		kernel32 = windll.kernel32
		handle = self.get_data_handle(format)
		GlobalSize = kernel32.GlobalSize
		GlobalSize.restype = c_uint32
		size = GlobalSize(handle)
		if handle == c_void_p(0) and get_last_error() != 0:
			raise WindowsError()
		data = create_string_buffer(size)  # '\0'���������Ă���
		GlobalLock = kernel32.GlobalLock
		GlobalLock.restype = c_void_p
		GlobalUnlock = kernel32.GlobalUnlock
		pointer = GlobalLock(handle)
		if pointer == c_void_p(0) and get_last_error() != 0:
			raise WindowsError()
		try:
			falconHelper.copyMemory(data, handle, size)
		finally:
			GlobalUnlock(pointer)
		return data.raw

	def get_ansi_text(self, encoding):
		data = self.get_data(ClipboardFormats.text.value)
		return data[0:len(data) - 1].decode(encoding)

	def get_unicode_text(self):
		data = self.get_data(ClipboardFormats.unicode_text.value)
		return data[0:len(data) - 2].decode("UTF-16")

	def get_dropped_files(self):
		kernel32 = windll.kernel32
		handle = self.get_data_handle(ClipboardFormats.drop_handle)
		GlobalSize = kernel32.GlobalSize
		GlobalSize.restype = c_uint32
		size = GlobalSize(handle)
		if handle == c_void_p(0) and get_last_error() != 0:
			raise WindowsError()
		data = create_string_buffer(size)  # '\0'���������Ă���
		GlobalLock = kernel32.GlobalLock
		GlobalLock.restype = c_void_p
		GlobalUnlock = kernel32.GlobalUnlock
		pointer = GlobalLock(handle)
		if pointer == c_void_p(0) and get_last_error() != 0:
			GlobalUnlock(pointer)
			raise WindowsError()
		#end if error
		num=win32api.DragQueryFile(pointer)
		lst=[]
		for i in range(num):
			lst.append(win32api.DragQueryFile(pointer,i))
		#end for
		GlobalUnlock(pointer)
		return lst
	#end get_dropped_file

	def set_data(self, format, data):
		user32 = windll.user32
		kernel32 = windll.kernel32
		GMEM_MOVEABLE = 0x0002
		GlobalAlloc = kernel32.GlobalAlloc
		GlobalAlloc.restype = c_void_p
		GlobalFree = kernel32.GlobalFree
		handle = GlobalAlloc(GMEM_MOVEABLE, len(data))
		if handle == c_void_p(0):
			raise WindowsError()

		try:
			GlobalLock = kernel32.GlobalLock
			GlobalLock.restype = c_void_p
			GlobalUnlock = kernel32.GlobalUnlock
			pointer = GlobalLock(handle)
			if pointer == c_void_p(0):
				raise WindowsError()
			try:
				falconHelper.copyMemory(pointer, data, len(data))
			finally:
				GlobalUnlock(handle)
			SetClipboardData = user32.SetClipboardData
			SetClipboardData.restype = c_void_p
			if SetClipboardData(format, handle) == c_void_p(0):
				raise WindowsError()
		except:
			GlobalFree(handle)
			raise
		return

	def set_ansi_text(self, data, encoding):
		if not isinstance(data, str):
			raise ArgumentError()
		buf = (data + "\0").encode(encoding)
		self.empty()
		self.set_data(ClipboardFormats.text.value, buf)
		return

	def set_unicode_text(self, data):
		if not isinstance(data, str):
			raise ArgumentError()
		buf=(data + "\0").encode("UTF-16")[2:]
		self.empty()
		self.set_data(ClipboardFormats.unicode_text.value, buf)
		return

	def empty(self):
		user32 = windll.user32
		EmptyClipboard = user32.EmptyClipboard
		if not EmptyClipboard():
			raise WindowsError()
		return

	def count_formats(self):
		user32 = windll.user32
		CountClipboardFormats = user32.CountClipboardFormats
		return CountClipboardFormats().raw

	def register_format(self, format_name):
		return win32clipboard.RegisterClipboardFormat(format_name)

	def get_formats(self):
		user32 = windll.user32
		EnumClipboardFormats = user32.EnumClipboardFormats
		fmt = EnumClipboardFormats(0)
		formats = array("i")
		while fmt != 0:
			formats.append(fmt)
			fmt = EnumClipboardFormats(fmt)
		return formats

	def is_format_available(self, format):
		user32 = windll.user32
		IsClipboardFormatAvailable = user32.IsClipboardFormatAvailable
		IsClipboardFormatAvailable.restype = c_bool
		return IsClipboardFormatAvailable(format_name).raw

	def get_format_name(self, format, expand_size=256):
		user32 = windll.user32
		GetClipboardFormatNameW = user32.GetClipboardFormatNameW
		buffer = create_unicode_buffer(expand_size)
		ret = GetClipboardFormatNameW(format, buffer, len(buffer))
		while ret + 1 == len(buffer):
			if get_last_error() != 0:
				raise WindowsError()
			buffer = create_unicode_buffer(len(buffer) + expand_size)
			ret = GetClipboardFormatNameW(format, buffer, len(buffer))
		return buffer.value


class ClipboardFormats(IntEnum):
	text = 1
	bitmap = 2
	metafilepict = 3
	ylk = 4
	dif = 5
	tiff = 6
	oem_text = 7
	dib = 8
	palette = 9
	pen_data = 10
	riff = 11
	wave = 12
	unicode_text = 13
	enhmetafile = 14
	drop_handle = 15
	locale = 16
	dib_v5 = 17
	owner_display = 0x0080
	dsp_text = 0x0081
	dsp_bitmap = 0x0082
	dsp_metafilepict = 0x0083
	dsp_enhmetafile = 0x008f
	private_first = 0x0200
	private_last = 0x02ff
	gdi_object_first = 0x0300
	gdi_object_last = 0x03ff
