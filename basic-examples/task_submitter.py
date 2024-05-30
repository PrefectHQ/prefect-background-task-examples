from tasks import my_background_task

if __name__ == "__main__":
    task_run = my_background_task.apply_async(args=["Agrajag"])
    print(task_run)
