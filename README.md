# Prefect Background Task Examples

This repository contains example applications that demonstrate how to use [Prefect](https://prefect.io) to run background tasks.

## Why use Prefect for background tasks?

Prefect tasks are a great way to quickly execute discrete units of work. When you call `delay()` or `apply_async()`, your tasks will run in a background process, on a task worker. This lets you move work out of the foreground of your application and distribute concurrent execution across multiple processes or machines.

For example, if you have a web app, you can use tasks to offload processes such as sending emails, processing images, or inserting data into a database.

In addition to providing a Pythonic interface for defining and running background tasks, Prefect scales up to advanced use cases, such as running tasks in parallel on Ray or Dask clusters, caching return values, configuring automatic retries, and building complex workflows with task dependencies.

## Using background tasks

Prefect tasks are Python functions that can be run immediately or submitted for background execution. 

You define a task by adding the `@task` decorator to a Python function, after which you can use the `delay` method to run the task in the background.

If you submit the task for background execution, you'll run a task worker in a separate process or container to execute the task. This process is similar to running a Celery or rq worker.

### Defining a task

Add the `@task` decorator to a Python function to define a Prefect task.
Here's an example:

```python
from prefect import task

@task
def my_background_task(name: str):
    # Task logic here
    print(f"Hello, {name}!")
```

### Calling tasks

You can call a task to run it immediately, or you can run it in the background with `Task.delay`.

**NOTE**: It is also possible to submit tasks to a _task runner_ such as Ray or Dask and run tasks in the background within a workflow, which in Prefect is called a _flow_. However, this document will focus on using background tasks outside of workflows. For example, by calling `my_task.delay()` within a web application.

However you run a task, Prefect will use your task configuration to manage and control task execution.
The following example shows both methods mentioned earlier, calling a task and using `delay`:

```python
# Import the previously-defined task
from my_tasks import my_background_task

# Run the task immediately
my_background_task("Joaquim")

# Schedule the task for execution outside of this process
my_background_task.delay("Agrajag")
```

For documentation on the features available for tasks, refer to the [Prefect Tasks documentation](https://docs.prefect.io/3.0/develop/write-tasks/).

### Running background tasks with a task worker

To run tasks in a separate process or container from where you schedule them with `delay`, start a task worker.

The task worker will continually receive background tasks to execute from Prefect's API, run them, and report the results back to the API.

**NOTE:** Task workers only run background tasks, not tasks you call directly.

You can run a task worker by calling `Task.serve` or passing task functions into the `prefect.task_worker.serve()` method, like in the following example *tasks.py* file:

```python
from prefect import task
from prefect.task_worker import serve


@task
def my_background_task(name: str):
    # Task logic here
    print(f"Hello, {name}!")


if __name__ == "__main__":
    # NOTE: The serve() function accepts multiple tasks. The task worker
    # will listen for background task runs for all tasks passed in.
    serve(my_background_task)
```

Run this script to start the task worker.

The task worker should begin listening for background tasks. If tasks were triggered before the task worker started, it will begin processing them.

**NOTE**: You can also use the CLI command `prefect task serve` to start a task worker.

## Guided exploration of background tasks and task workers in Prefect

Below we explore increasingly realistic examples of using background tasks and task workers in Prefect.

We'll start by running a Prefect task in the foreground by calling it.

Next we'll start a task worker and trigger some tasks to run in the background. We'll see how we can use multiple task workers to run tasks in parallel.

Then we'll create a basic FastAPI application that triggers background tasks when you hit an endpoint.

Next we'll use Docker in two examples that mimic real use cases.
One example uses a FastAPI server with multiple microservices and simulates a new user signup workflow.
The other example uses a Flask server with [Marvin](https://www.askmarvin.ai/) to ask questions of an LLM from the CLI and get back answers.

The examples build on the ones that come before.
After setting up your environment, feel free to skip ahead if you're already familiar with the basics.

### Setup

<details> <summary>Expand</summary>

Step 1: Activate a virtual environment

The following example uses [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html), but any virtual environment manager will work.

```bash
conda deactivate
conda create -n python-tasks python=3.12
conda activate python-tasks
```

Step 2: Install Python dependencies

```bash
pip install -U prefect marvin fastapi==0.107
```

Step 3: Connect to Prefect Cloud or a local Prefect server instance (if not set already)

You can use either Prefect Cloud or a local Prefect server instance for these examples.

You need to have `PREFECT_API_URL` set to submit tasks to task servers.

If you're using a local Prefect server instance with a SQLite backing database (the default database), you can save this value to your active Prefect Profile by running the following command in your terminal.

```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

If using Prefect Cloud, set the `PREFECT_API_URL` value to the Prefect Cloud API URL and add your [API key](https://docs.prefect.io/3.0/manage/cloud/manage-users/api-keys#manage-api-keys).

The examples that use docker (examples 4 and 5) use a local Prefect server instance by default.
You can switch to Prefect Cloud by changing the `PREFECT_API_URL` and adding a variable for your API key in the `docker-compose.yaml`.
Or use a local server instance backed by a PostgreSQL database by setting the `PREFECT_API_DATABASE_CONNECTION_URL`.

If using a local Prefect server instance instead of Prefect Cloud, start your server by running the following command:

```bash
prefect server start 
```

Step 4: Clone the repository (optional)

You can code from scratch or clone the repository to get the code files for the examples.

```bash
git clone https://github.com/PrefectHQ/prefect-background-task-examples.git
```

Move into the directory.

```bash
cd prefect-background-task-examples
```

Let's run some tasks!
</details>

### Example 1: Run a Prefect task in the foreground by calling it

<details> <summary>Expand</summary>

Add the `@task` decorator to any Python function to define a Prefect task.

Step 1: Create a file named `greeter.py` and save the following code in it:

```python
from prefect import task 

@task(log_prints=True)
def greet(name: str = "Marvin"):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

Step 2: Run the script in the terminal.

```bash
python greeter.py
```

You should see the task run in the terminal. This task runs in the foreground. In other words, it is not running in the background.

#### Optional

You can see the task run in the UI.
If you're using a self-hosted Prefect Server instance, you can also see the task runs in the database.

If you want to inspect the SQLite database, use your favorite interface.
We explain how to use *DB Browser for SQLite* below.

Download it [here](https://sqlitebrowser.org/dl/), if needed. Install it and open it.

Click *Connect*. Then navigate to your SQLite DB file. It will be in the `~/.prefect` directory by default.

Head to the `task_run` table and you should see all your task runs there.
You can scroll down to see your most recent task runs or filter for them.

Hit the refresh button for updates, if needed.

</details>

### Example 2: Start a task worker and run tasks in the background

<details> <summary>Expand</summary>

In this example, we'll start a task worker and run background tasks.  

To run tasks in a separate process or container from where you trigger them, you'll start a task worker.

The task worker will continually receive submitted tasks to execute from Prefect's API, run them, and report the results back to the API.
You can run a task worker by passing tasks into the `prefect.task_worker.serve()` method.

Step 1: Define the task and task worker in the file `task_worker.py`

```python
from prefect import task
from prefect.task_worker import serve


@task
def my_background_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    serve(my_background_task)
```

Step 2: Start the task worker by running the script in the terminal.

```bash
python task_worker.py
```

The task worker is now waiting for runs of the `my_background_task` task.
Let's give it some task runs.

Step 3: Create a file named `task_submitter.py` and save the following code in it.

```python
from tasks import my_background_task

if __name__ == "__main__":
    my_background_task.delay("Agrajag")
```

Step 4: Open another terminal and run the script.

```bash
python task_submitter.py
```

Note that we return a "future" from the `delay` method. You can use this object to wait for the task to complete with `wait()` and to retrieve its result with `result()`.
We can also see the task run's UUID and other information about the task run.

Step 5: See the task run in the UI.

Open Prefect's UI and navigate to the Runs page. Select "Tasks" to see a list of task runs. You should see your new task in the list.

Step 6: You can use multiple task workers to run tasks in parallel.

Start another instance of the task worker. In another terminal run:

```bash
python task_worker.py
```

Step 7: Submit multiple tasks to the task worker.

Modify the `task_submitter.py` file to submit multiple tasks to the task worker with different inputs:

```python
from tasks import my_background_task

if __name__ == "__main__":
    my_background_task.delay("Ford")
    my_background_task.delay("Prefect")
    my_background_task.delay("Slartibartfast")
```

Run the file and watch the work get distributed across both task workers!

Step 8: Shut down the task servers with *control* + *c*.

Alright, you can submit tasks to multiple Prefect task workers running in the background!
This is cool because we can observe these tasks executing in parallel and very quickly with web sockets - no polling required.

</details>

### Example 3: Create a basic FastAPI server that triggers background tasks

<details> <summary>Expand</summary>

Step 1: Define API routes for the FastAPI server in a Python file.

Let's define two routes for our FastAPI server.
The first is a basic hello world route at the root URL to confirm that the FastAPI server is working.
The second route, `/task`, will trigger a background task when the `http://127.0.0.1:8000/task` URL is hit and return information about the task.

Here are the contents of `first_fastapi.py`:

```python
from fastapi import FastAPI
from prefect import task
from fastapi_tasks import my_fastapi_task

app = FastAPI()


@app.get("/")
def greet():
    print(f"Hello, world!")
    return f"Hello, world!"


@app.get("/task")
async def prefect_task():
    future = my_fastapi_task.delay("Trillian")
    return {"message": f"Prefect Task submitted: {future.task_run_id}"}
```

Step 2: Define a Prefect task worker in a Python file.

Here are the contents of `fastapi_tasks.py`:

```python
from prefect import task
from prefect.task_worker import serve


@task(log_prints=True)
def my_fastapi_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    serve(my_fastapi_task)
```

Step 3: Start a FastAPI server that hot reloads when code changes with the following command:

```bash
uvicorn first_fastapi:app --reload
```

Step 4: Start the Prefect task worker.

In another terminal, run the following command to start the task worker.

```bash
python fastapi_tasks.py
```

Step 5: Navigate to `http://127.0.0.1:8000/task` in the browser to submit a task!

You should see the info for the submitted task returned in the browser.

Step 6: Stop the server and worker.

Hit `control` + `c` in the respective terminals to stop the server and worker.

You've seen how to use a FastAPI web server to offload work to a Prefect task worker - all while gaining observability into the task runs in the Prefect UI.
Next, let's use Docker containers with more advanced workflows to move toward productionizing our code.

</details>

### Example 4: Use Docker to run a FastAPI server and a Prefect task worker

<details> <summary>Expand</summary>

The following example will simulate a new user signup workflow with multiple services.
We'll run a Prefect server instance, a Prefect task worker, and a FastAPI server in separate Docker containers.

All the code files for this example live in the `fastapi-user-signups` directory.
We've defined the FastAPI server, model, and tasks in Python files.
The Makefile and docker-compose files are used to wire everything together.

Step 1: Upgrade Docker to the latest version, if you aren't already using it.

Step 2: Move into the `fastapi-user-signups` directory.

Step 3: Run `make` to build the Docker images.

Step 4: Run `docker compose up` to fire everything up.

The services should start and everything should run.
If you have issues and do some troubleshooting, you can then run the following commands to try to rebuild and fire up the services.

```bash
make clean
make
docker compose up
```

Step 5: Send a new user signup to the FastAPI server.

From your terminal, run the following command to send a new user signup to the FastAPI server.

```bash
curl -X POST http://localhost:8000/users --header "Content-Type: application/json" --data '{"email": "chris.g@prefect.io", "name": "Guidry"}'
```

Step 6: Explore the tasks by checking out the Docker containers.

Inspect the Docker containers and you should see that the Prefect server instance, task worker, and FastAPI server are running.

There are multiple services that are engaged when the API URL is reached.
Check out the Python files and the docker-compose.yml file to see how the services are set up.

</details>

### Example 5: Use Docker to run a Flask server and a Prefect task worker to ask an LLM questions with Marvin

<details> <summary>Expand</summary>

Step 1: Move into the `flask-task-monitoring` directory.

Step 2: Grab an API key from OpenAI and create an `.openai.env` file in the `flask-task-monitoring` top directory with the following contents:

```
OPENAI_API_KEY=my_api_key_goes_here
```

Step 3: Run `make` to pull the Docker images and build the containers.

```bash
make
```

Step 4: Run `docker compose up` to start the server and worker in the containers.

```bash
docker compose up
```

Troubleshoot as needed following the process in Example 4.

Step 5: Submit questions to Marvin via Flask.

Use the following command to run the script in the `ask.py` file and ask Marvin a question.

```bash
python ask.py "What is the meaning of life?"
```

You should receive a text answer to your question.
Have fun asking Marvin other deep questions.

</details>
