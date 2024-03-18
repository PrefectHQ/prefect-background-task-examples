# Prefect Background Tasks

This repository contains example applications that demonstrate how to use [Prefect](https://prefect.io) to run background tasks.
See the [Tutorial](./tutorial/) for step-by-step instructions showing progressively more advanced use cases.

## Why use Prefect background tasks?

Prefect background tasks are a great way to quickly execute discrete units of work in background processes.
For example, if you have a web app, you can use Prefect background tasks to offload processes such as sending emails, processing images, or inserting data into a database.
Prefect background tasks are ideal for a microservices architecture, where you have a number of small, independent services that need to communicate with each other.
With Prefect, you can run tasks in parallel, cache return values, configure automatic retries, and more, with a simple interface that scales up to complex workflows that need dynamic infrastructure.

## Why Prefect instead of Celery or arq?

If you are familiar with tools like Celery and arq, Prefect offers a similar Pythonic interface for defining and running tasks, plus a host of other benefits including:

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

## Using tasks

Prefect tasks are Python functions that can be run immediately or submitted for background execution, similar to arq or Celery tasks.
You define a task by adding the `@task` decorator to a Python function, after which you can use one of several methods to run the task.

If you submit the task for background execution, you'll run a task server in a separate process or container to execute the task.
This process is similar to how you would run a Celery worker or an arq worker to execute background tasks.

### This feature is experimental

Historically, tasks in Prefect could only be called within a [flow](https://docs.prefect.io/latest/concepts/flows/).
Flows have a set of features similar to "Canvas" workflows in Celery or Directed Acyclic Graphs (DAGs) in batch
processing systems such as Airflow.

Calling and submitting tasks outside of flows is currently **experimental**.
To use this feature, set the `PREFECT_EXPERIMENTAL_ENABLE_TASK_SCHEDULING` setting to `true`:

```bash
prefect config set PREFECT_EXPERIMENTAL_ENABLE_TASK_SCHEDULING=true
```

**NOTE**: With this setting turned on, you can use tasks without flows both when using an open-source Prefect API server or with Prefect Cloud.

The Prefect team is actively working on this feature and would love to hear your feedback.
Let us know what you think in the [Prefect Community Slack](https://communityinviter.com/apps/prefect-community/prefect-community).

## Getting started

Head to the [Tutorial](./tutorial/) to get started!
