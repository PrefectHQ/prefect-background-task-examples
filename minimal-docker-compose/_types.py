from typing import Any

from pydantic import BaseModel


class JobRequest(BaseModel):
    job_id: str
    job_type: str
    payload: dict[str, Any]
