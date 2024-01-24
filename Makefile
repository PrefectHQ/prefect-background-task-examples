.DEFAULT_GOAL := all
.PHONY: all clean test tests

virtualenvs:
	for d in *; do \
		echo $$d;
	done

all:
	$(MAKE) -C fastapi-user-signups $@

clean:
	$(MAKE) -C fastapi-user-signups $@

tests:
	$(MAKE) -C fastapi-user-signups $@
test: tests
