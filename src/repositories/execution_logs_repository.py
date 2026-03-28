from typing import Any
from src.repositories.base_repository import BaseMongoRepository


class ExecutionLogsRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "execution_logs"

    @property
    def indexes(self) -> list[dict[str, Any]]:
        return [
            {"key": [("process_name", 1)]},
            {"key": [("created_at", -1)]},
        ]

    async def create_log(self, data: dict[str, Any]):
        return await self.collection.insert_one(data)
