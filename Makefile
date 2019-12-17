.PHONY: all test release build nuke.pth

all: .venv build nuke.pth docs/build/html/*

build: docs/build/html/.git lib/site-packages

ifeq ($(OS), Windows_NT)
PYTHON27?=py -2.7
NUKE_PYTHON?="C:/Program\ Files/Nuke10.5v7/python.exe"
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
endif


requirements.txt: pyproject.toml
	poetry export -f requirements.txt --output requirements.txt
	# https://github.com/python-poetry/poetry/issues/897
	sed -i 's/^-e //g' requirements.txt 

lib/site-packages: requirements.txt
	rm -rf lib/site-packages
	$(PYTHON27) -m pip install -r requirements.txt --target lib/site-packages

docs/.git:
	git fetch -fn origin docs:docs
	git worktree add -f docs docs

docs/build/html/.git:
	git fetch -fn origin gh-pages:gh-pages
	rm -rf docs/build/html
	git worktree add -f docs/build/html gh-pages

docs/*: docs/.git

docs/build/html/*: docs/build/html/.git .venv docs/*
	. ./scripts/activate-venv.sh &&\
		$(MAKE) -C docs html

test: build
	. ./scripts/activate-venv.sh && python -m pytest tests

release:
	standard-version

nuke.pth: .venv
	$(NUKE_PYTHON) -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $$(./scripts/get-venv-python-lib.sh)/nuke.pth

.venv: pyproject.toml
	poetry install
	touch .venv/.make_success


