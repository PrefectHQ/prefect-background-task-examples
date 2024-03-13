.DEFAULT_GOAL := all
.PHONY: all clean test tests

virtualenvs:
	for d in *; do \
		echo $$d;
	done

all:
	$(MAKE) -C chaos-duck $@
	$(MAKE) -C fastapi-user-signups $@
	$(MAKE) -C flask-task-monitoring $@

clean:
	$(MAKE) -C chaos-duck $@
	$(MAKE) -C fastapi-user-signups $@
	$(MAKE) -C flask-task-monitoring $@

tests:
	$(MAKE) -C chaos-duck $@
	$(MAKE) -C fastapi-user-signups $@
	$(MAKE) -C flask-task-monitoring $@

test: tests
