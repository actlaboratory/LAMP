# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
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

def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

appveyor=False
BASE_PACKAGE_URL="dummy"

if len(sys.argv)==2 and sys.argv[1]=="--appveyor":
	appveyor=True

print("Starting build (appveyor mode=%s)" % appveyor)
build_filename=os.environ['APPVEYOR_REPO_TAG_NAME'] if 'APPVEYOR_REPO_TAG_NAME' in os.environ else 'snapshot'
print("Will be built as %s" % build_filename)

pyinstaller_path="pyinstaller.exe" if appveyor is False else "%PYTHON%\\Scripts\\pyinstaller.exe"
if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

if os.path.isdir("dist\\lamp"):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")
	shutil.rmtree("build\\")

print("Building...")
runcmd("%s --windowed --log-level=ERROR lamp.py" % pyinstaller_path)

shutil.copytree("locale\\","dist\\lamp\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
shutil.copytree("fx\\", "dist\\lamp\\fx")
for elem in glob.glob("public\\*"):
	if os.path.isfile(elem):
		shutil.copyfile(elem,"dist\\lamp\\%s" % os.path.basename(elem))
	else:
		shutil.copytree(elem,"dist\\lamp\\%s" % os.path.basename(elem))
#end copypublic

print("Compressing into package...")
shutil.make_archive("lamp-%s" % (build_filename),'zip','dist')

if build_filename=="snapshot":
	print("Skipping batch archiving because this is a snapshot release.")
else:
	print("Making patch...")
	archiver=diff_archiver.DiffArchiver(BASE_PACKAGE_URL,"lamp-%s.zip" % (build_filename),"lamp-%spatch" % (build_filename),clean_base_package=True, skip_root = True)
	archiver.work()
	print("creating version info file...")
	with open("lamp-%s.zip" % (build_filename), mode = "rb") as f:
		content = f.read()
		package_hash = hashlib.sha1(content).hexdigest()
	with open("lamp-%spatch.zip" % (build_filename), mode = "rb") as f:
		content = f.read()
		patch_hash = hashlib.sha1(content).hexdigest()
	with open("lamp-%s_info.json" % (build_filename), mode = "w") as f:
		info = {
			"package_hash": package_hash,
			"patch_hash": patch_hash
		}
		json.dump(info, f)
print("Build finished!")
