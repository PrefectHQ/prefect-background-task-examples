# background tasks minimal setup

This repo contains a minimal example of how to use background tasks with Prefect.

The example is a simple API that submits a payload to a background task, but the pattern could easily be expanded.

## Overview

- `minimal_setup/api.py` - a simple API that submits a payload to a background task
- `minimal_setup/tasks.py` - a background task that processes the payload
- `minimal_setup/requirements.txt` - a list of dependencies
- `minimal_setup/test` - a script that tests the API and background task

## Running the example manually
See the [test script](./test) for a quick way to run the example.

See the rest of the repo for containerized examples.