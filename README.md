# Prefect task scheduling examples

This repo houses example applications using Prefect Tasks for common background
processing use cases.  The examples here should be self-contained applications that can
run locally and have both automated integration tests included.  In most cases,
`prefect` would be designated to install from a local development repo (assumed to be
a sibling directory of this one).

It's recommended to create a `virtualenv` for each directory, as they may all be using
different underlying packages.  While you can do this with any virtual environment
tool, `pyenv` makes this a breeze to keep track of by switching automatically for you:

```bash
cd fastapi-user-signups
pyenv virtualenv 3.12.1 tse-fastapi-user-signups
pyenv local tse-fastapi-user-signups
```

If you are a `pyenv` user, you can run the script `./create-all-virtualenvs` to do this
on your behalf.

## Getting the applications set up

```bash
make
```

This will install the Python dependencies for each application.  If using `pyenv`, this
will be applied to the virtualenv configured for each directory.

## Running the application and its dependencies for local interaction

Each application defines its runtime dependencies like databases or other servers in a
`docker-compose.yaml` file, so you will generally use `docker compose` to interact with
them.  Some common patterns:

```bash
docker compose up
```

Running the application in this way will mount your local working copy of `prefect` so
that you can use these tests on an unreleased local copy of `prefect`.

## Running the application's test suite

```bash
docker compose run --rm tests
```

And to pass arguments to `pytest`:

```bash
docker compose run --rm tests -f -ff
```

To run the tests in all of the example applications:

```bash
make tests
```
