.PHONY: all test release build

all: .venv build docs/build/html

build: docs/build/html/.git lib/site-packages

ifeq ($(OS), Windows_NT)
PYTHON27?=py -2.7
NUKE_PYTHON?="C:/Program Files/Nuke10.5v7/python.exe
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
endif


requirements.txt: pyproject.toml
	poetry export -f requirements.txt --output requirements.txt
	# https://github.com/python-poetry/poetry/issues/897
	sed -i 's/^-e //g' requirements.txt 

# https://github.com/pypa/pip/issues/5735
lib/site-packages: export PIP_NO_BUILD_ISOLATION=false
lib/site-packages: requirements.txt
	rm -rf lib/site-packages
	$(PYTHON27) -m pip install -r requirements.txt --target lib/site-packages

docs/.git:
	git fetch -fn origin docs:docs
	git worktree add -f docs docs

docs/build/html/.git: docs/.git
	git fetch -fn origin gh-pages:gh-pages
	rm -rf docs/build/html
	git worktree add -f docs/build/html gh-pages

docs/*: docs/.git

docs/build/html: .venv docs/build/html/.git docs/*
	. ./scripts/activate-venv.sh &&\
		"$(MAKE)" -C docs html
	touch docs/build/html

test: .venv lib/site-packages
	. ./scripts/activate-venv.sh && python -m pytest tests

release:
	standard-version

.venv: export POETRY_VIRTUALENVS_IN_PROJECT=true
.venv: pyproject.toml
	poetry env use "$(PYTHON27)"
	poetry run python -m pip install -U pip
	poetry run python -m pip install -U more-itertools==5.0.0 poetry
	poetry install
	$(NUKE_PYTHON) -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $$(./scripts/get-venv-python-lib.sh)/nuke.pth
	touch .venv


