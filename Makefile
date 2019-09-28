
# Recursively call parser Makefile
parser_%:
	cd parser && make $(patsubst parser_%,%,$@)

env:
	virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt

test_parser:
	@python3 -m unittest discover -s tests/parser -p '*.py' -t . -v

test:
	@python3 -m unittest discover -s tests -p '*.py' -t .

.PHONY: test

