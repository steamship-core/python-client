# Makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
LAZYDOCSBUILDDIR      = _lazy_docs_build
AUTODOCDIR    = api
DOCSDIR      = ../../python-docs/pages

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $?), 1)
$(error "The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/")
endif

.PHONY: help clean Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)/* $(AUTODOCDIR)

markdown:
	pip install -r ../requirements.txt
	pip install -r ../requirements.dev.txt
	pip install -r ./requirements.txt
	rm -rf $(BUILDDIR)/markdown
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	mkdir -p $(BUILDDIR)/markdown/client-reference
	rm -rf $(BUILDDIR)/markdown/api
	find "../../python-docs/pages" -type d -empty -delete
	find "../../python-docs/pages" -type f ! -name "_meta.json" -delete
	cp -R $(BUILDDIR)/markdown/* $(DOCSDIR)
	./rename_index.sh
	rm -rf $(DOCSDIR)/_sphinx_design_static/
	find $(DOCSDIR) -name '*.md' -exec sed -i '' 's/(\([^)]*.png\))/(\/\1)/g' {} \;
	lazydocs  --output-path=$(LAZYDOCSBUILDDIR) --overview-file="steamship.md" --src-base-url="https://github.com/steamship-core/python-client/tree/main/" ../src/
	rm -f $(LAZYDOCSBUILDDIR)/.pages
	mkdir -p $(DOCSDIR)/client-reference/steamship
	cp -R $(LAZYDOCSBUILDDIR)/* $(DOCSDIR)/client-reference/steamship
	mv $(DOCSDIR)/client-reference/steamship/steamship.md $(DOCSDIR)/client-reference/steamship.md
	sed -i '' 's|(./|(./steamship/|g' $(DOCSDIR)/client-reference/steamship.md

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	pip install -r ../requirements.txt
	pip install -r ../requirements.dev.txt
	pip install -r ./requirements.txt
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
