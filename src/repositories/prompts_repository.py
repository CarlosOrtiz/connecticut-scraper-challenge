from typing import Any
from src.repositories.base_repository import BaseMongoRepository


class PromptsRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "prompts"

    @property
    def indexes(self) -> list[dict[str, Any]]:
        return [{"key": [("key", 1)], "unique": True}]

    async def get_prompts(self) -> list[dict[str, Any]]:
        cursor = self.collection.find({"status": "active"})
        return await cursor.to_list(length=None)
