
# Recursively call parser Makefile
parser_%:
	cd parser && make $(patsubst parser_%,%,$@)

env:
	virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt
.PHONY: env

test_parser test_common test_verifier test_runner:
	@python3 -m unittest discover -s tests/$(patsubst test_%,%,$@) -p '*.py' -t . -v
.PHONY: test_parser test_common test_verifier test_runner

test:
	@python3 -m unittest discover -s tests -p '*.py' -t .

.PHONY: test

