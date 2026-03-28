from typing import Any
from pymongo import UpdateOne
from src.repositories.base_repository import BaseMongoRepository


class ForeclosuresRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "foreclosures"

    @property
    def indexes(self) -> list[dict[str, Any]]:
        return [{"key": [("town", 1)], "unique": True}]

    async def get_existing_towns(self) -> set[str]:
        towns = await self.collection.distinct("town")
        return {
            town.strip().upper()
            for town in towns
            if isinstance(town, str) and town.strip()
        }

    async def bulk_upsert_towns(self, towns_data: list[dict[str, Any]]):
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
