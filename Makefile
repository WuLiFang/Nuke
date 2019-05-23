.PHONY: all test release

all: lib/site-packages docs docs/build/html

lib/site-packages: .venv requirements.txt
	.venv/Scripts/activate; python -m pip install -U pip
	.venv/Scripts/activate; python -m pip install --target="lib/site-packages" --upgrade -r "requirements.txt"

docs:
	git worktree add -f --checkout docs docs

docs/build/html:
	git worktree add -f --checkout docs/build/html gh-pages

test:
	.venv/Scripts/activate; python -m pytest tests

release:
	standard-version
