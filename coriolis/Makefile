PEP8FILES = common/*.py parser/*.py runner/*.py tests/*.py verifier/*.py
PEP8FLAGS = -v -v -v --in-place --aggressive --aggressive --aggressive --max-line-length 200


# Recursively call parser Makefile
parser_%:
	cd parser && make $(patsubst parser_%,%,$@)

env:
	virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt
.PHONY: env

lint:
	@autopep8 ${PEP8FLAGS} ${PEP8FILES}

test_parser test_common test_verifier test_runner: lint
	@python3 -m unittest discover -b -s tests/$(patsubst test_%,%,$@) -p '*.py' -t . -v
.PHONY: test_parser test_common test_verifier test_runner

test: lint
	@python3 -m unittest discover -b -s tests -p '*.py' -t .
.PHONY: test

docker-image:
	docker build -f docker/Dockerfile -t coriolis:latest .
