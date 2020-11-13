.PHONY: default test release build docs/build/html

default: .venv build docs/build/html

build: docs/build/html/.git lib/site-packages

ifeq ($(OS), Windows_NT)
PYTHON27?=C:\Python27\python.exe
NUKE_PYTHON?=C:/Program Files/Nuke10.5v7/python.exe
# abspath not work on windows
PYTHON_LIB=.venv/Lib/site-packages/
PYTHONPATH:=$(PYTHONPATH);lib/site-packages;lib;../lib/site-packages;../lib
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
PYTHON_LIB=$(abspath .venv/lib/python2.7/site-packages/)
PYTHONPATH:=$(PYTHONPATH):$(abspath lib/site-packages):$(abspath lib)
endif

export PYTHONPATH

requirements.txt: pyproject.toml
	poetry export --without-hashes --dev --output requirements.txt

# https://github.com/pypa/pip/issues/5735
lib/site-packages: export PIP_NO_BUILD_ISOLATION=false
lib/site-packages: requirements.txt
	rm -rf lib/site-packages
	"$(PYTHON27)" -m pip install -U poetry==1.1.4
	"$(PYTHON27)" -m pip install -r requirements.txt --target lib/site-packages

docs/.git:
	git fetch -fn origin docs:docs
	git worktree add -f docs docs

docs/build/html/.git: docs/.git
	git fetch -fn origin gh-pages:gh-pages
	rm -rf docs/build/html
	git worktree add -f docs/build/html gh-pages

docs/*: docs/.git

docs/build/html: .venv docs/build/html/.git
	poetry run "$(MAKE)" -C docs html

test: .venv lib/site-packages
	poetry run pytest tests

release:
	standard-version

.venv: export POETRY_VIRTUALENVS_IN_PROJECT=true
.venv: pyproject.toml
	poetry env use "$(PYTHON27)"
	"$(NUKE_PYTHON)" -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > "$(PYTHON_LIB)/nuke.pth"
	touch .venv


