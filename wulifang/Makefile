ifeq ($(OS), Windows_NT)
PYTHON27?=C:\Python27\python.exe
NUKE_PYTHON?=C:/Program Files/Nuke10.5v7/python.exe
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
endif

vendor/__init__.py: vendor-requirements.txt
	# Do not run this in vscode integrated terminal before windows 10 1803
	# https://github.com/microsoft/vscode/issues/36630
	"$(PYTHON27)" -m pip install -r vendor-requirements.txt --target vendor --upgrade
	touch $@
