# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019 - 2020 guredora <contact@guredora.com>

import glob
import os
import sys
import subprocess
import shutil
import distutils.dir_util
import PyInstaller
import diff_archiver
import hashlib
import json
import sys
sys.path.append(os.getcwd())
import constants

def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

appveyor=False

if len(sys.argv)==2 and sys.argv[1]=="--appveyor":
	appveyor=True
print("Starting build for %s(appveyor mode=%s)" % (constants.APP_NAME, appveyor))
build_filename=os.environ['APPVEYOR_REPO_TAG_NAME'] if 'APPVEYOR_REPO_TAG_NAME' in os.environ else 'snapshot'
print("Will be built as %s" % build_filename)

pyinstaller_path="pyinstaller.exe" if appveyor is False else "%PYTHON%\\Scripts\\pyinstaller.exe"
hooks_path = os.path.join(PyInstaller.__path__[0], "hooks/")
print("hooks_path is %s" % (hooks_path))
print("pyinstaller_path=%s" % pyinstaller_path)
if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

package_path = os.path.join("dist", os.path.splitext(os.path.basename(constants.STARTUP_FILE))[0])
if os.path.isdir(package_path):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")
	shutil.rmtree("build\\")

print("Building...")
for hook in constants.NEED_HOOKS:
	shutil.copy(hook, hooks_path)
runcmd("%s --windowed --log-level=ERROR %s" % (pyinstaller_path, constants.STARTUP_FILE))

shutil.copytree("locale\\","dist\\SOC\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
for item in constants.PACKAGE_CONTAIN_ITEMS:
	if os.path.isdir(item):
		shutil.copytree(item, os.path.join(package_path, item))
	if os.path.isfile(item):
		shutil.copyfile(item, os.path.join(package_name, os.path.basename(item)))
for elem in glob.glob("public\\*"):
	if os.path.isfile(elem):
		shutil.copyfile(elem,"dist\\SOC\\%s" % os.path.basename(elem))
	else:
		shutil.copytree(elem,"dist\\SOC\\%s" % os.path.basename(elem))
#end copypublic

print("Compressing into package...")
shutil.make_archive("%s-%s" % (constants.APP_NAME, build_filename),'zip','dist')

if build_filename=="snapshot":
	print("Skipping batch archiving because this is a snapshot release.")
else:
	if constants.BASE_PACKAGE_URL is not None:
		print("Making patch...")
		archive_name = "%s-%s.zip" % (constants.APP_NAME, build_filename)
		patch_name = "%s-%spatch" % (constants.APP_NAME, build_filename)
		archiver=diff_archiver.DiffArchiver(constants.BASE_PACKAGE_URL, archive_name, patch_name,clean_base_package=True, skip_root = True)
		archiver.work()
		print("computing hash...")
		with open(archive_name, mode = "rb") as f:
			content = f.read()
			package_hash = hashlib.sha1(content).hexdigest()
		with open(patch_name+".zip", mode = "rb") as f:
			content = f.read()
			patch_hash = hashlib.sha1(content).hexdigest()
		print("creating package info...")
		with open("%s-%s_info.json" % (constants.APP_NAME, build_filename), mode = "w") as f:
			info = {
				"package_hash": package_hash,
				"patch_hash": patch_hash
			}
			json.dump(info, f)
print("Build finished!")
