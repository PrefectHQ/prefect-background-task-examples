.DEFAULT_GOAL := install
.PHONY: all install clean test tests

requirements_in = $(filter-out MANIFEST.in, $(wildcard *.in))
requirements_out := $(requirements_in:.in=.txt)

PIP_VERSION=24.0
PIP_TOOLS_VERSION=7.3.0

all: $(requirements_out) install

.bookkeeping/pip-$(PIP_VERSION):
	mkdir -p .bookkeeping && touch $@.next

	python -m pip install pip==$(PIP_VERSION) wheel

	mv $@.next $@

.bookkeeping/pip-tools-$(PIP_TOOLS_VERSION): .bookkeeping/pip-$(PIP_VERSION)
	mkdir -p .bookkeeping && touch $@.next

	python -m pip install pip-tools==$(PIP_TOOLS_VERSION)

	mv $@.next $@

.PHONY: .bookkeeping/pip-tools
.bookkeeping/pip-tools: .bookkeeping/pip-tools-$(PIP_TOOLS_VERSION)

.bookkeeping/development.txt: .bookkeeping/pip-tools-$(PIP_TOOLS_VERSION) requirements-dev.txt
	mkdir -p .bookkeeping
	cp requirements-dev.txt $@.next

	pip-sync $@.next
	docker compose build

	mv $@.next $@

requirements.txt: requirements.in .bookkeeping/pip-tools-$(PIP_TOOLS_VERSION)
	pip-compile --no-strip-extras \
		requirements.in --output-file $@

requirements-dev.txt: requirements.txt requirements-dev.in
	pip-compile --no-strip-extras \
		requirements.txt requirements-dev.in --output-file $@

upgrade-packages:
	pip-compile --no-strip-extras --upgrade \
		requirements.in --output-file requirements.txt
	pip-compile --no-strip-extras --upgrade \
		requirements.txt requirements-dev.in --output-file requirements-dev.txt

install: .bookkeeping/development.txt
bump: upgrade-packages all

.PHONY: uninstall
uninstall:
	pip uninstall -y prefect prefect_cloud $$(pip freeze | grep -v 'git+')
	rm -f .bookkeeping/development.txt
	python -m pip install pip-tools==$(PIP_TOOLS_VERSION)

.PHONY: reinstall
reinstall: uninstall install

clean:
	rm -Rf .bookkeeping/


tests:
	docker compose run --rm tests

test: tests
