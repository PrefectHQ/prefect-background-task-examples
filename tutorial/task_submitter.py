from task_server import my_background_task

if __name__ == "__main__":
    val = my_background_task.submit("Agrajag")
    print(val)
