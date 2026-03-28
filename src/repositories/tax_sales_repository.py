from typing import Any
from pymongo import UpdateOne
from src.repositories.base_repository import BaseMongoRepository


class TaxSalesRepository(BaseMongoRepository):
    @property
    def collection_name(self) -> str:
        return "tax_sales"

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

    async def upsert_tax_sale(self, tax_sale_data: dict[str, Any]):
        return await self.collection.update_one(
            {"town": tax_sale_data["town"]},
            {"$set": tax_sale_data},
            upsert=True,
        )

    async def bulk_upsert_tax_sales(self, tax_sales_data: list[dict[str, Any]]):
        operations = [
            UpdateOne({"town": item["town"]}, {"$set": item}, upsert=True)
            for item in tax_sales_data
            if item.get("town")
        ]
        if not operations:
            return None
        return await self.collection.bulk_write(operations)
