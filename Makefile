.PHONY: default test build docs/build/html

ifeq ($(OS), Windows_NT)
PYTHON27?=C:\Python27\python.exe
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

default: .venv build docs/build/html $(VENV_SITEPATH)/lib.pth

build: docs/build/html/.git lib/site-packages/.sentinel

export PYTHONPATH
export PYTHONIOENCODING=

# https://github.com/pypa/pip/issues/5735
lib/site-packages/.sentinel: export PIP_NO_BUILD_ISOLATION=false
lib/site-packages/.sentinel: requirements.txt patches/*.patch
	rm -rf lib/site-packages
	"$(PYTHON27)" -m pip install -r requirements.txt --target lib/site-packages
	rm -rfv lib/site-packages/**/*.pyc
	for file in patches/*.patch; do patch -p1 < $$file; done
	touch $@

docs/.git:
	git fetch -fn origin docs:docs
	git worktree add -f docs docs

docs/build/html/.git: docs/.git
	git fetch -fn origin gh-pages:gh-pages
	rm -rf docs/build/html
	git worktree add -f docs/build/html gh-pages

docs/*: docs/.git

docs/build/html: .venv/.sentinel lib/site-packages/.sentinel docs/build/html/.git
	. ./scripts/activate-venv.sh &&\
		"$(MAKE)" -C docs html

.venv:
	virtualenv --python "$(PYTHON27)" --clear .venv
	touch $@

$(VENV_SITEPATH)/nuke.pth:
	"$(NUKE_PYTHON)" -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $@

$(VENV_SITEPATH)/lib.pth: lib/site-packages/.sentinel
	./scripts/add-lib-path.sh

.venv/.sentinel: .venv dev-requirements.txt $(VENV_SITEPATH)/nuke.pth $(VENV_SITEPATH)/lib.pth
	. ./scripts/activate-venv.sh &&\
		pip install -U -r dev-requirements.txt
	touch $@

test: .venv/.sentinel
	. ./scripts/activate-venv.sh &&\
		pytest
