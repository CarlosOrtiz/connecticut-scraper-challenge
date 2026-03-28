import json
from typing import Any
from src.repositories.execution_logs_repository import ExecutionLogsRepository


async def consume_execution_log(record: dict[str, Any]):
    body = json.loads(record["body"])
    message = json.loads(body["Message"])

    repo = ExecutionLogsRepository()
    await repo.create_log(message)
