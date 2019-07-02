.PHONY: all test release

all: lib/site-packages docs docs/build/html .venv/lib/site-packages/lib.pth

ifeq ($(OS), Windows_NT)
PYTHON27?=C:/Python27/python.exe
else
PYTHON27?=python2.7
endif


lib/site-packages: .venv/lib/site-packages/.make_sucess requirements.txt
	rm -rf lib/site-packages
	. ./scripts/activate-venv.sh &&\
		python -m pip install -U pip urllib3[secure] &&\
		pip install --target="lib/site-packages" --upgrade -r "requirements.txt"

.venv/lib/site-packages/lib.pth: lib/site-packages

	echo ../../../lib > .venv/lib/site-packages/lib.pth
	echo ../../../lib/site-packages >> .venv/lib/site-packages/lib.pth

docs:
	git worktree add -f --checkout docs docs

docs/build/html:
	git worktree add -f --checkout docs/build/html gh-pages

test:
	. ./scripts/activate-venv.sh && python -m pytest tests

release:
	standard-version

.venv/lib/site-packages/.make_sucess: dev-requirements.txt .venv/.make_sucess
	. ./scripts/activate-venv.sh && pip install -r dev-requirements.txt
	echo > .venv/lib/site-packages/.make_sucess

.venv/.make_sucess: $(PYTHON27)
	virtualenv .venv --python $(PYTHON27)
	echo > .venv/.make_sucess
