# Prefect Background Task Examples

This repository contains examples applications that demonstrate how to use Prefect to
run background tasks. The examples include a FastAPI application that processes user
signups and a Flask application that handles image uploads. Each example is
self-contained, can be run locally, and includes automated tests.

## Why Prefect instead of Celery or arq?

If you are familiar with tools like Celery and arq, Prefect offers a similar Pythonic
interface for defining and running tasks, paired with a robust set of features:

- Support for asynchronous and synchronous Python
- A rich UI and CLI for observing and managing task execution
- Configurable retries, timeouts, error handling, caching, concurrency control, result
  storage, and more
- An interface that scales from background tasks to complex schedule- and event-driven
  workflows
- Metrics, events, incidents, automations, and other advanced features for monitoring and
  managing tasks and workflows
- A free and open-source version, an enterprise-grade Cloud for scheduling tasks
  without managing infrastructure, and a self-hosted Cloud offering
- A growing ecosystem of integrations

Next, we'll provide a brief introduction to defining and running tasks with Prefect.

## Using Tasks

Prefect tasks are Python functions that can be run immediately or submitted for background
execution, similar to arq or Celery tasks. You define a task by adding the `@task`
decorator to a Python function, after which you can use one of several methods to run the
task.

If you submit the task for background execution, you'll run a Task Server in a separate
process or container to execute the task. This is similar to how you would run a Celery
worker or an arq worker to execute background tasks.

### This Feature is Experimental

Historically, tasks in Prefect could only be called within a
[flow](https://docs.prefect.io/latest/concepts/flows/). Flows have a set of features
similar to "Canvas" workflows in Celery or Directed Acyclic Graphs (DAGs) in batch
processing systems such as Airflow.

Calling and submitting tasks outside of flows is currently **experimental**.
To use this feature, set the `PREFECT_EXPERIMENTAL_ENABLE_TASK_SCHEDULING` setting to `true`:

```bash
prefect config set PREFECT_EXPERIMENTAL_ENABLE_TASK_SCHEDULING=true
```

**NOTE**: With this setting turned on, you can use tasks without flows both when using an open-source Prefect API server and with Prefect Cloud.

The Prefect team is actively working on this feature and would love to hear your feedback.
Let us know what you think in the [Prefect Community Slack](https://communityinviter.com/apps/prefect-community/prefect-community).


### Defining a Task

Add the `@task` decorator to a Python function to define a Prefect task. Here's an
example:

```python
from prefect import task

@task
def my_background_task(name: str):
    # Task logic here
    print(f"Hello, {name}!")
```

### Calling Tasks

You can call a task to run it immediately, use `Task.map()` to run many invocations of the
same task with different inputs, or submit the task for background execution with
`Task.submit()`.

**TIP:** For Celery users, `Task.submit()` is similar to `Task.delay()` or
`Task.apply_async()`. For arq users, it's similar to `Task.enqueue()`.

In all three cases, Prefect will use your task configuration to manage and control task
execution. The following example shows all three methods:

```python
# Import the previously-defined task
from my_tasks import my_background_task

# Run the task immediately
my_background_task("Joaquim")

# Run the task multiple times with different inputs
my_background_task.map(["Joaquim", "Marta", "Aiden"])

# Submit the task for execution outside of this process
my_background_task.submit()

# You can also run the task immediately without Prefect features like configurable
# retries and timeouts:
my_background_task.fn("Andrew")
```

For comprehensive documentation on the features available for tasks, refer to the [Prefect
Tasks documentation](https://docs.prefect.io/latest/concepts/tasks/).

### Executing Background Tasks with a Task Server

To run tasks in a separate process or container, you'll need to start a Task Server, similar to
how you would run a Celery worker or an arq worker.

The Task Server will continually receive submitted tasks to execute from Prefect's API,
execute them, and report the results back to the API. You can run a Task Server by passing
tasks into the `prefect.task_server.serve()` method, like so:

```python
from prefect import task
from prefect.task_server import serve


@task
def my_background_task(name: str):
    # Task logic here
    print(f"Hello, {name}!")


if __name__ == "__main__":
    # NOTE: The serve() function accepts multiple tasks. The Task Server 
    # will listen for submitted task runs for all tasks passed in.
    serve(my_background_task)
```

Once this file exists, you can use it to run the Task Server. If the name of the file is
`tasks.py`, you'll run `python tasks.py`. The Task Server should start and begin listening
for submitting tasks. If tasks were submitted before the Task Server started, it will
begin processing them.

## Getting Started with the Example Applications

Now that you have a basic introduction to defining and running background tasks with
Prefect, let's explore the example applications in this repository.

### Setting Up Your Environment

We recommend creating a separate virtual environment for each example application. We've
included a script that uses `pyenv` to create virtual environments.

If you are using `pyenv`, running the `./create-all-virtualenvs` script can automate the
setup process for all provided examples:

```bash
./create-all-virtualenvs
```

### Installing Dependencies

To install the required Python dependencies for each example application, run
`make` from the root of the repository:

```bash
make
```

This command installs all necessary dependencies within the virtual environment for each
example application. If using `pyenv`, the dependencies will be installed into the
virtualenv configured for each directory.

## Running and Testing the Applications

Each example comes with a `docker-compose.yaml` file to define runtime dependencies like
databases. You can use `docker compose` to run the example applications and their tests.

### Running the Applications

To run an example application along with its dependencies, use the following command from
the directory containing the application:

```bash
docker compose up
```

This method allows for local testing and interaction with the example applications.

### Running Tests

To run the automated test suite for an example application:

```bash
docker compose run --rm tests
```

And to pass additional arguments to `pytest`:

```bash
docker compose run --rm tests -f -ff
```

For executing tests across all example applications, run `make tests` from the root of the
repository.

```bash
make tests
```
