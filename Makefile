.PHONY: default test build docs/_build/html deploy-docs

ifeq ($(OS), Windows_NT)
PYTHON27?=C:/Python27/python.exe
NUKE_PYTHON?=C:/Program Files/Nuke10.5v7/python.exe
# abspath not work on windows
VENV_SITEPATH=.venv/Lib/site-packages
PYTHONPATH:=$(PYTHONPATH);lib/site-packages;lib;../lib/site-packages;../lib
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
VENV_SITEPATH=$(abspath .venv/lib/python2.7/site-packages/)
PYTHONPATH:=$(PYTHONPATH):$(abspath lib/site-packages):$(abspath lib)
endif

default: .venv/.sentinel build docs/_build/html $(VENV_SITEPATH)/lib.pth 

build: docs/_build/html lib/site-packages/.sentinel wulifang/vendor/__init__.py

export PYTHONPATH
export PYTHONIOENCODING=UTF-8


# https://github.com/pypa/pip/issues/5735
lib/site-packages/.sentinel: export PIP_NO_BUILD_ISOLATION=false
lib/site-packages/.sentinel: requirements.txt
	# Do not run this in vscode integrated terminal before windows 10 1803
	# https://github.com/microsoft/vscode/issues/36630
	rm -rf lib/site-packages
	"$(PYTHON27)" -m pip install -r requirements.txt --target lib/site-packages
	find lib/site-packages -name *.pyc -print -delete
	touch $@

docs/_build/html: PYTHONPATH=
docs/_build/html:
	"$(MAKE)" -C docs html


$(VENV_SITEPATH)/nuke.pth:
	"$(NUKE_PYTHON)" -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $@

$(VENV_SITEPATH)/lib.pth: lib/site-packages/.sentinel
	./scripts/add-lib-path.sh

.venv: PYTHONPATH=
.venv:
	virtualenv --python "$(PYTHON27)" --clear .venv

.venv/.sentinel: .venv dev-requirements.txt $(VENV_SITEPATH)/nuke.pth $(VENV_SITEPATH)/lib.pth
	. ./scripts/activate-venv.sh &&\
		pip install -U -r dev-requirements.txt
	touch $@

wulifang/vendor/__init__.py:
	$(MAKE) -C wulifang

test: .venv/.sentinel wulifang/vendor/__init__.py
	. ./scripts/activate-venv.sh &&\
		pytest

