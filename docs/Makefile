# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile deploy

docx: 
	@$(SPHINXBUILD) -M epub "$(SOURCEDIR)" "$(BUILDDIR)" -t docx $(SPHINXOPTS) $(O)
	-mkdir -p _build/docx
	pandoc --data-dir .pandoc -o _build/docx/sphinx.docx _build/epub/sphinx.epub

deploy: REMOTE?="$(realpath ..)"
deploy: html
	cd $(BUILDDIR)/html &&\
		set -ex &&\
		rm -rf .git &&\
		git init &&\
		git add --all &&\
		git fetch $(REMOTE) gh-pages &&\
		if [ -z "$$(git diff --shortstat FETCH_HEAD)" ]; then echo "Already up to date" && exit 0; fi &&\
		git commit -m "chore: deploy docs" &&\
		git push -f $(REMOTE) HEAD:gh-pages

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@echo "${PYTHONPATH}"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
