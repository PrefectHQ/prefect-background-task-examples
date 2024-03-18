from tasks import my_background_task

if __name__ == "__main__":
    task_run = my_background_task.submit("Agrajag")
    print(task_run)
