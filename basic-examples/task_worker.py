from prefect.task_worker import serve
from tasks import my_background_task


if __name__ == "__main__":
    serve(my_background_task)
