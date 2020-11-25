import wx, itertools, sys, winreg, logging
import globalVars, shellapi, constants

def setAssoc(extension, associate=None, mimetype=None):
	if not hasattr(sys,"frozen"): return False
	if extension[0] != ".": extension = "." + extension
	if associate == None: associate = "actlab.%s" % constants.APP_NAME
	return _registerFileAssociation(extension, sys.executable, associate, mimetype)

def unsetAssoc(associate=None):
	if associate == None: associate = "actlab.%s" % constants.APP_NAME
	unregisterAddonFileAssociation(associate)

def _registerFileAssociation(extension, exePath, associate, mimetype):
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
	except WindowsError as e:
		log = logging.getLogger("%s.fileAssoc" % (constants.LOG_PREFIX))
		log.error("file Association faild - %s" %(str(e)))
		return False

def unregisterAddonFileAssociation(associate):
	try:
		_deleteKeyAndSubkeys(winreg.HKEY_CURRENT_USER, "Software\\Classes\\%s" % associate)
	except WindowsError as e:
		log = logging.getLogger("%s.fileAssoc" % (constants.LOG_PREFIX))
		log.error("Unset File Association faild - %s" %str(e))
		return False
	shellapi.SHChangeNotify(shellapi.SHCNE_ASSOCCHANGED, shellapi.SHCNF_IDLIST, None, None)
	return True

def _deleteKeyAndSubkeys(key, subkey):
	log = logging.getLogger("%s.fileAssoc" % (constants.LOG_PREFIX))
	isOpen = False
	tryCount = 0
	while not isOpen and tryCount <= 10:
		try:
			with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE|winreg.KEY_READ) as k:
				isOpen = True
				log.debug("del_reg_open - %s" %(str(k)))
				for i in itertools.count():
					isOpen1 = False
					tryCount1 = 0
					while not isOpen1 and tryCount1 <= 10:
						try:
							isOpen1 = True
							subkeyName = winreg.EnumKey(k, i)
							log.debug("del_reg_get - %s" %(subkeyName))
						except Exception as e:
							tryCount1 += 1
							log.debug("del_reg_get - %s" %(str(e)))
							break
						_deleteKeyAndSubkeys(k, subkeyName)
				isOpen2 = False
				tryCount2 = 0
				while not isOpen2 and tryCount2 <= 10:
					try:
						isOpen2 = True
						winreg.DeleteKey(k, "")
						log.debug("del_reg_del - %s" %(k))
					except Exception as e:
						tryCount2 += 1
						log.error("delete_regKey \"%s\" - %s" %(k, e))
		except:
			tryCount += 1

