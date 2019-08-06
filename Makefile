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
	$(PYTHON27) -m pip install --target="lib/site-packages" -r "requirements.txt"
	./scripts/add-lib-path.sh
	echo > lib/site-packages/.make_sucess

docs/.git:
	git fetch -fn origin docs:docs
	git worktree add -f docs docs

docs/build/html/.git: docs/.git lib/site-packages/.make_sucess
	git fetch -fn origin gh-pages:gh-pages
	rm -rf docs/build/html
	git worktree add -f docs/build/html gh-pages

docs: docs/* docs/build/html/.git
	. ./scripts/activate-venv.sh &&\
		$(MAKE) -C docs html

test: lib/site-packages/.make_sucess
	. ./scripts/activate-venv.sh && echo $${PYTHONPATH}
	. ./scripts/activate-venv.sh && python -m pytest tests

release:
	standard-version

.venv:
	virtualenv --python $(NUKE_PYTHON) .venv

.venv/.make_sucess: .venv dev-requirements.txt docs/requirements.txt
	$(PYTHON27) -m pip install --target "$$(./scripts/get-venv-python-lib.sh)" -r dev-requirements.txt -r docs/requirements.txt
	$(NUKE_PYTHON) -c 'import imp;import os;print(os.path.dirname(imp.find_module("nuke")[1]))' > $$(./scripts/get-venv-python-lib.sh)/nuke.pth
	echo > .venv/.make_sucess

docs/requirements.txt: docs/.git

docs/*: docs/.git
