import uvicorn
from cachetools import TTLCache
from fastapi import FastAPI

from _types import JobRequest
from tasks import process_job

app = FastAPI()

job_cache: TTLCache = TTLCache(maxsize=100, ttl=60)


@app.post("/job")
def submit_job(job_request: JobRequest):
    future = process_job.delay(job_request)
    job_cache[job_request.job_id] = future
    return {"message": "Job submitted"}


@app.get("/job/{job_id}")
def read_job(job_id: str):
    return job_cache[job_id]


@app.get("/jobs")
def read_jobs():
    return list(job_cache.keys())


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
