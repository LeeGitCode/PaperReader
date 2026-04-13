from typing import Any
from uuid import uuid4

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.registry import parse_url


TASKS: dict[str, dict[str, Any]] = {}


def create_task() -> str:
    task_id = str(uuid4())
    TASKS[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "result": None,
        "error_msg": None,
    }
    return task_id


def get_task(task_id: str) -> dict[str, Any] | None:
    return TASKS.get(task_id)


async def run_parse_task(task_id: str, source: str) -> None:
    task = TASKS[task_id]
    task.update({"status": "processing", "progress": 20, "error_msg": None})

    try:
        task["progress"] = 45
        result = await parse_url(source)
        task.update(
            {
                "status": "completed",
                "progress": 100,
                "result": result,
                "error_msg": None,
            }
        )
    except PaperParseError as exc:
        task.update(
            {
                "status": "failed",
                "progress": 100,
                "result": None,
                "error_msg": str(exc),
            }
        )
    except Exception as exc:
        task.update(
            {
                "status": "failed",
                "progress": 100,
                "result": None,
                "error_msg": f"解析任务失败：{exc.__class__.__name__}",
            }
        )
