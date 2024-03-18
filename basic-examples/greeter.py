from prefect import task


@task(log_prints=True)
def greet(name: str = "Marvin"):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    greet()
