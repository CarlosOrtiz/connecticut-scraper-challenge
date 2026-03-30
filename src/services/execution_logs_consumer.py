from typing import Any

from src.repositories.execution_logs_repository import ExecutionLogsRepository


async def create_execution_log(message: dict[str, Any]) -> None:
    repo = ExecutionLogsRepository()
    await repo.create_log(message)
