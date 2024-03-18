# Exploring Prefect Background Task Examples

This tutorial will familiarize you with Prefect background tasks and task servers.

In this tutorial, we'll explore increasingly realistic examples of using Prefect background tasks.

We'll start by running a Prefect task outside of a flow.
Previously, Prefect tasks could only be run inside a flow.
Now, you can run tasks outside of a flow. The only restriction on tasks is that a task cannot call another task.

Then we'll start a task server and run tasks in the background.
We'll see how we can use multiple task servers to run tasks in parallel.

Then we create our first basic FastAPI application that submits tasks to a Prefect task server when you hit an endpoint.

Then we'll move to using Docker with two examples that mimic real use cases.
One example uses a FastAPI server with multiple microservices and simulates a new user signup workflow.
The other example uses a Flask server with Marvin to ask an LLM questions from the CLI and get back answers.

Each example builds on the ones that come before.
After setting up your environment, feel free to skip ahead if you're already familiar with the basics.

## Examples

1. Run a Prefect task outside of a flow
1. Start a task server (or two) and run tasks in the background
1. Create a basic FastAPI server tha offloads work by submitting tasks to a Prefect task server
1. Use Docker to run a FastAPI server and a few Prefect task servers with a new user signup workflow
1. Use Docker to run a Flask server and a Prefect task server with Marvin and ask an LLM questions

## Setup

### Step 1: Activate a virtual environment

The following example uses [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html), but any virtual environment manager will work.

```bash
conda deactivate
conda create -n python-tasks python=3.12
conda activate python-tasks
```

### Step 2: Install Python dependencies

```bash
pip install -U prefect marvin fastapi==0.107
```

### Step 3: Set your Prefect profile to use experimental task scheduling

```bash
prefect config set PREFECT_EXPERIMENTAL_ENABLE_TASK_SCHEDULING=true
```

### Step 4: Connect to Prefect Cloud or a local Prefect server instance

You can use either Prefect Cloud or a local Prefect server instance for these examples.

You need to have `PREFECT_API_URL`set to use background task servers.

If you're using a local Prefect server instance with a SQLite backing database (the default database), you can save this value to your active Prefect Profile by running the following command in your terminal.

```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

If using Prefect Cloud, you can set the `PREFECT_API_URL` value to the Prefect Cloud API URL and add your API key.

The Docker examples (Examples 4 and 5) use a local Prefect server instance by default.
You can switch to Prefect Cloud by changing the `PREFECT_API_URL` and adding a variable for your API key in the `docker-compose.yaml`.
Or use a local server instance backed by a PostgreSQL database by setting the `PREFECT__DATABASE__CONNECTION_URL`.Start your Prefect server instance.

If using a local Prefect server instance instead of Prefect Cloud, start your server by running the following command:

```bash
prefect server start 
```

### Step 5: Clone the repository (optional)

You can code from scratch or clone the repository to get the code files for the examples.

```bash
git clone https://github.com/PrefectHQ/prefect-background-task-examples.git
```

Move into the directory.

```bash
cd prefect-background-task-examples
```

Alright, let's run some tasks!

## Example 1: Run a Prefect task outside of a flow

Add the `@task` decorator to any Python function to define a Prefect task.

Step 1: Create a file named `greeter.py` and save the following code in it.

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

You should see the task run in the terminal.

Optional:

You can see the task run in the UI (when the task run page is implemented - coming soon!).
If you're using a self-hosted Prefect Server instance, you can also see the task runs in the database.

If yo want to inspect the SQLite database, use your favorite interface.
We show how to use *DB Browser for SQLite* below.

Download it [here](https://sqlitebrowser.org/dl/), if needed. Install it and open it.

Click *Connect*. Then navigate to your SQLite DB file. It will be in the `~/.prefect` directory by default.

Head to the `task_run` table and you should see all your task runs there.
You can scroll down to see your most recent task runs or filter for them.

Hit the refresh button for updates, if needed.

## Example 2: Start a task server and run tasks in the background

In this example, we'll start a task server and run tasks in the background.  

To run tasks in a separate process or container, you'll need to start a task server, similar to how you would run a Celery worker or an arq worker.
The task server will continually receive submitted tasks to execute from Prefect's API, execute them, and report the results back to the API.
You can run a task server by passing tasks into the `prefect.task_server.serve()` method.

Step 1: Define the task and task server in the file `task_server.py`

```python
from prefect import task
from prefect.task_server import serve


@task
def my_background_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    # if on prefect 2.16.4 or older add the following line
    # from task_server import my_background_task

    serve(my_background_task)
```

Step 2: Start the task server by running the script in the terminal.

```bash
python task_server.py
```

The task server is now waiting for runs of the my_background_task task.
Let's give it some task runs.

Step 3: Create a file named `task_submitter.py` and save the following code in it.

```python
from task_server import my_b_task

if __name__ == "__main__":
    val = my_b_task.submit("Agrajag")
    print(val)
```

Step 4: Open another terminal and run the script.

```bash
python task_submitter.py
```

**TIP:** For Celery users, `Task.submit()` is similar to `Task.delay()` or
`Task.apply_async()`. For arq users, it's similar to `Task.enqueue()`.

Note that we return the task run object from the `submit` method.
This way we can see the task run UUID and other information about the task run.

Step 5: See the task run in the UI.

Use the task run UUID to see the task run in the UI.
The URL will look like this:

<http://127.0.0.1:4200/task-runs/task-run/my_task_run_uuid_goes_here>

Substitute your UUID at the end of the URL.
Note that the UI navigation experience for task runs will be improved soon.

Step 6: You can use multiple task servers to run tasks in parallel.

Start another instance of the task server.

In another terminal run:

```bash
python task_server.py
```

Step 7: Submit multiple tasks to the task server with `map`.

Modify the `task_submitter.py` file to submit multiple tasks to the task server with different inputs by using the `map` method.

```python
from task_server import my_b_task

if __name__ == "__main__":
    my_b_task.map(["Ford", "Prefect", "Slartibartfast"])
```

Run the file and watch the work get distributed across both task servers!

Step 8: Shut down the task servers with *control* + *c*

Alright, you're able to submit tasks to multiple Prefect task servers running in the background!
This is cool because we can observe these tasks executing in parallel and very quickly with web sockets - no polling required.

Next, let's wire up our task server to a FastAPI task server.

## Example 3: Create a basic FastAPI server that submits tasks to a Prefect task server

Step 1: Define API routes for the FastAPI server in a Python file.

Let's define two routes for our FastAPI server.
The first is a basic hello world route at the root URL to confirm that the FastAPI server is working.
The second route, `/task`, will submit a task to the Prefect task server when the URL is hit and return information about the submitted task.
You could name this route whatever you like.

Here are the contents of [first_fastapi.py](./first_fastapi.py)

```python
from fastapi import FastAPI
from prefect import task
from first_fastapi_task_server import my_fastapi_task

app = FastAPI()


@task
def my_b_task(name: str):
    print(f"Hello, {name}!")
    return f"Hello, {name}!"


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/task")
async def prefect_task():
    val = my_fastapi_task.submit(name="Marvin")
    return {"message": f"Prefect Task submitted: {val}"}
```

Step 2: Define a Prefect task server in a Python file.

Here are the contents of [ff_prefect_task_server.py](./ff_prefect_task_server.py)

```python
from prefect import task
from prefect.task_server import serve


@task
def my_fastapi_task(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    serve(my_fastapi_task)
```

Step 3: Start a FastAPI server that hot reloads when code changes with the following command:

```bash
uvicorn first_fastapi:app --reload
```

Step 4: Start the Prefect Task server.

In another terminal, run the following command to start the Prefect Task server.

```bash
python ff_prefect_task_server.py
```

Step 5: Navigate to `http://127.0.0.1:8000/task` in the browser to submit a task!

You should see the info for the submitted task returned in the browser.

Step 6: Stop the servers.

Hit `control` + `c` in the respective terminals to stop the servers.

You've seen how to use a FastAPI web server to offload work to a a Prefect task server - all while gaining observability into the task runs in the Prefect UI.
Next, let's use Docker containers with more advanced workflows to move toward productionizing our code.

## Example 4: Use Docker to run a FastAPI server and a Prefect task server

The following example will simulate a new user signup workflow with multiple services.
We'll run a Prefect server instance, a Prefect task server, and a FastAPI server in separate Docker containers.

All the code files for this example live in the [`fastapi-user-signups` directory](../fastapi-user-signups).
We've defined the FastAPI server, model, and tasks in Python files.
The Makefile and docker-compose files are used to wire everything together.

Step 1: Upgrade Docker to the latest version, if you aren't already using it.

Step 2: Move into the [`fastapi-user-signups` directory](../fastapi-user-signups/).

Step 3: Run `make` to build the Docker images.

Step 4: Run `docker compose up` to fire everyting up.

The services should start and everything should run.
If you have issues and do some troubleshooting, you can then run the following commands to try to rebuild and fire up the services.

```bash
make clean
make
docker compose up
```

Step 5: Send a new user signup to the FastAPI server.

From you terminal, run the following command to send a new user signup to the FastAPI server.

```bash
curl -X POST http://localhost:8000/users --header "Content-Type: application/json" --data '{"email": "chris.g@prefect.io", "name": "Guidry"}'
```

Step 6: Explore the tasks by checking out the Docker containers.

Inspect the Docker containers and you should see that the Prefect server instance, task server, and FastAPI server are running.

There are multiple services that are engaged when the API URL is reached.
Check out the Python files and the docker-compose.yml file to see how the services are set up.

## Example 5: Use Docker to run a Flask server and a Prefect task server with Marvin

This example will allow us to ask Marvin questions and get answers from a Flask server.
This example showcases working with an LLM and a different w

Step 1: Move into the *flask-task-monitoring* directory.

Step 2: Grab an API key from OpenAI and create an *.openai.env* file in the *flask-task-monitoring* top directory with the following contents:

```
OPENAI_API_KEY=my_api_key_goes_here
```

Step 3: Run `make` to pull the Docker images and build the containers.

Step 4: Run `docker compose up` to start the servers in the containers.

Troubleshoot as needed following the process in Example 4.

Step 5: Submit questions to Marvin via Flask.

Use the following command to run the script at in the `ask.py` file and ask Marvin a question.

```bash
python ask.py "What is the meaning of life?"
```

You should receive an text answer to your question.
Have fun asking Marvin other questions.

## Next steps

Way to go!
You've seen how to use Prefect to run background tasks with a Prefect task server and several web servers.

There's lots more you can do with Prefect background tasks.
We can't wait to see what you build!
