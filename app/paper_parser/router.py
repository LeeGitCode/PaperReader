from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.paper_parser.tasks import create_task, get_task, run_parse_task


router = APIRouter(prefix="/tasks", tags=["paper-parser"])


class ParseTaskCreate(BaseModel):
    url: str = Field(min_length=1)


class ParseTaskCreated(BaseModel):
    task_id: str


@router.post("/parse", response_model=ParseTaskCreated)
def create_parse_task(payload: ParseTaskCreate, background_tasks: BackgroundTasks) -> dict[str, str]:
    task_id = create_task()
    background_tasks.add_task(run_parse_task, task_id, payload.url)
    return {"task_id": task_id}


@router.get("/{task_id}")
def get_task_status(task_id: str) -> dict[str, Any]:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task
