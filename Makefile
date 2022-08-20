PYTHON = python3

.PHONY: help uncache filetrans

help:       ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

uncache:    ## Remove __pycache__ directories
	find . -type d -name  "__pycache__" -exec rm -r {} +

filetrans:  ## filetrans
	cp script/$@.py .
	$(PYTHON) $@.py
	rm $@.py
