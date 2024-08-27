.DEFAULT_GOAL := install
.PHONY: all install clean test tests lock sync upgrade

requirements_in := requirements.in requirements-dev.in
requirements_out := requirements.txt requirements-dev.txt

UV_VERSION := latest

all: lock install

.bookkeeping/uv-$(UV_VERSION):
	mkdir -p .bookkeeping
	curl -LsSf https://astral.sh/uv/install.sh | sh
	touch $@

lock: .bookkeeping/uv-$(UV_VERSION)
	uv pip compile requirements.in -o requirements.txt
	uv pip compile requirements.txt requirements-dev.in -o requirements-dev.txt

sync: .bookkeeping/uv-$(UV_VERSION) $(requirements_out)
	uv pip sync requirements-dev.txt

install: sync

upgrade: .bookkeeping/uv-$(UV_VERSION)
	uv pip compile requirements.in -o requirements.txt --upgrade
	uv pip compile requirements.txt requirements-dev.in -o requirements-dev.txt --upgrade

uninstall:
	uv pip uninstall -y -r requirements-dev.txt

reinstall: uninstall install

clean:
	rm -rf .bookkeeping/

tests:
	python -m pytest

test: tests