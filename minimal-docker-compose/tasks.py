from prefect import task

from _types import JobRequest


@task
def process_job(job_request: JobRequest):
    print(f"Processing job {job_request.job_id}")
    print(f"Job type: {job_request.job_type}")
    print(f"Payload: {job_request.payload}")

    return {"message": "Job processed successfully"}


if __name__ == "__main__":
    process_job.serve()
