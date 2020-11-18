import wx, itertools, sys, winreg, logging
import globalVars, shellapi, constants

def setAssoc(extension, associate=None, content=None):
	if not hasattr(sys,"frozen"): return False
	if extension[0] != ".": extension = "." + extension
	if associate == None: associate = "actlab.%s" % constants.APP_NAME
	return _registerFileAssociation(extension, sys.executable, associate, content)

def unsetAssoc(associate=None):
	if associate == None: associate = "actlab.%s" % constants.APP_NAME
	unregisterAddonFileAssociation(associate)

def _registerFileAssociation(extension, exePath, associate, content):
	try:
		with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Classes\\%s" % associate, 0, winreg.KEY_WRITE) as k:
			#winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "")
			with winreg.CreateKeyEx(k, "DefaultIcon", 0, winreg.KEY_WRITE) as k2:
				winreg.SetValueEx(k2, None, 0, winreg.REG_SZ, "@{exePath},1".format(exePath=exePath))
			with winreg.CreateKeyEx(k, "shell\\open\\command", 0, winreg.KEY_WRITE) as k2:
				winreg.SetValueEx(k2, None, 0, winreg.REG_SZ, u"\"{exePath}\" \"%1\"".format(exePath=exePath))
		with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Classes\\%s" % extension, 0, winreg.KEY_WRITE) as k:
			winreg.SetValueEx(k, None, 0, winreg.REG_SZ, associate)
			if mimetype != None: winreg.SetValueEx(k, "Content Type", 0, winreg.REG_SZ, mimetype)
			k2 = winreg.CreateKeyEx(k, "OpenWithProgids\\%s" % associate, 0, winreg.KEY_WRITE)
			winreg.CloseKey(k2)
		shellapi.SHChangeNotify(shellapi.SHCNE_ASSOCCHANGED, shellapi.SHCNF_IDLIST, None, None)
		return True
	except WindowsError:
		log = logging.getlogger(constants.LOG_PREFIX, "fileAssoc")
		log.error("Can not create addon file association.", exc_info=True)
		return False

def unregisterAddonFileAssociation(associate):
	try:
		_deleteKeyAndSubkeys(winreg.HKEY_CURRENT_USER, "Software\\Classes\\%s" % associate)
	except WindowsError:
		return
	shellapi.SHChangeNotify(shellapi.SHCNE_ASSOCCHANGED, shellapi.SHCNF_IDLIST, None, None)

def _deleteKeyAndSubkeys(key, subkey):
	with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE|winreg.KEY_READ) as k:
		for i in itertools.count():
			try:
				subkeyName = winreg.EnumKey(k, i)
			except WindowsError:
				break
			_deleteKeyAndSubkeys(k, subkeyName)
		winreg.DeleteKey(k, "")
