PYTHON = python3

.PHONY: uncache filetrans

uncache:
	find . -type d -name  "__pycache__" -exec rm -r {} +

filetrans:
	cp script/$@.py .
	$(PYTHON) $@.py
	rm $@.py
