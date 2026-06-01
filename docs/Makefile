SPHINXBUILD ?= sphinx-build

.PHONY: html html-zh html-en sphinx-zh sphinx-en clean

html: html-zh html-en

html-zh:
	build-docs -l zh_CN

html-en:
	build-docs -l en

sphinx-zh:
	$(SPHINXBUILD) -b html zh_CN _build/zh_CN/html

sphinx-en:
	$(SPHINXBUILD) -b html en _build/en/html

clean:
	rm -rf _build

