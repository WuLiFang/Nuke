.PHONY: all test release

all: lib/site-packages/.make_sucess docs docs/build/html 

ifeq ($(OS), Windows_NT)
PYTHON27?=py -2.7
NUKE_PYTHON?=C:/Program\ Files/Nuke10.5v7/python.exe
else
PYTHON27?=/usr/bin/python
NUKE_PYTHON?=python
endif


lib/site-packages/.make_sucess: .venv/.make_sucess requirements.txt
	rm -rf lib/site-packages
	$(PYTHON27) -m pip install --target="lib/site-packages" --upgrade -r "requirements.txt"
	./scripts/add-lib-path.sh
	echo > lib/site-packages/.make_sucess

docs:
	git worktree add -f --checkout docs docs

docs/build/html:
	git worktree add -f --checkout docs/build/html gh-pages

test: lib/site-packages/.make_sucess
	. ./scripts/activate-venv.sh && echo $${PYTHONPATH}
	. ./scripts/activate-venv.sh && python -m pytest tests

release:
	standard-version

.venv/.make_sucess: dev-requirements.txt 
	virtualenv --python $(NUKE_PYTHON) .venv
	$(PYTHON27) -m pip install --target "$$(./scripts/get-python-lib.sh)" -r dev-requirements.txt
	$(NUKE_PYTHON) -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $$(./scripts/get-python-lib.sh)/nuke.pth
	echo > .venv/.make_sucess

temp:

