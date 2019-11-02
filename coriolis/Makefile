GIT_SHA := $(shell git rev-parse HEAD | cut -c 1-12)
VERSION := 1.0-$(shell git describe --tags --dirty --always --abbrev=12)
COVERAGE_OMIT := */venv/*,*/__init__.py,tests/*

PWD := $(shell pwd)

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
	@coverage run --omit ${COVERAGE_OMIT} -m unittest discover -b -s tests/$(patsubst test_%,%,$@) -p '*.py' -t . -v && coverage report
.PHONY: test_parser test_common test_verifier test_runner

test: lint
	@coverage run --omit ${COVERAGE_OMIT} -m unittest discover -b -s tests -p '*.py' -t . && coverage report
.PHONY: test

docker-image:
	docker build -f docker/Dockerfile --build-arg VERSION=$(VERSION) -t coriolis:$(VERSION) .

build:
	docker run --rm -v ${PWD}/bin:/mnt coriolis:${VERSION} bash -c "cp dist/* /mnt"
