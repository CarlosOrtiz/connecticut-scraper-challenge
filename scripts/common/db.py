from typing import Any
from aws_python_helper import Repository
from pymongo import UpdateOne

from scripts.common.config import get_settings

settings = get_settings()


class BaseMongoRepository(Repository):
    @property
    def database_key(self) -> str:
        return settings.MONGO_DB_NAME


class PromptsRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "prompts"


class ForeclosuresRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "foreclosures"

    @property
    def indexes(self):
        return [{"key": [("town", 1)], "unique": True}]

    async def get_existing_towns(self):
        towns = await self.collection.distinct("town")
        return {
            town.upper() for town in towns if isinstance(town, str) and town.strip()
        }

    async def bulk_upsert_towns(self, towns_data: list[dict[str, Any]]) -> Any | None:
        operations = []

        for town_data in towns_data:
            town = town_data.get("town")

            if not isinstance(town, str) or not town.strip():
                continue

            normalized_town = town.strip().upper()
            payload = {**town_data, "town": normalized_town}

            operations.append(
                UpdateOne({"town": normalized_town}, {"$set": payload}, upsert=True)
            )

        if not operations:
            return None

        return await self.collection.bulk_write(operations)
