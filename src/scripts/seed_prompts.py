import asyncio
import os
import sys

from aws_python_helper import MongoManager

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.common.config import get_settings  # noqa: E402
from src.repositories.prompts_repository import PromptsRepository  # noqa: E402


settings = get_settings()
MongoManager.initialize(settings.MONGO_URI)


PROMPTS = [
    {
        "key": "amount_due",
        "question": "Extract the total amount due for this property from the document. Return only the numeric value without currency symbols.",
        "schema": {
            "type": "object",
            "properties": {
                "amount_due": {"type": "string"},
            },
            "required": ["amount_due"],
        },
        "status": "active",
    },
    {
        "key": "property_address",
        "question": "Extract the full property address from this tax sale document.",
        "schema": {
            "type": "object",
            "properties": {
                "property_address": {"type": "string"},
            },
            "required": ["property_address"],
        },
        "status": "active",
    },
]


async def main() -> None:
    repo = PromptsRepository()

    for prompt in PROMPTS:
        await repo.collection.update_one(
            {"key": prompt["key"]},
            {"$set": prompt},
            upsert=True,
        )

    print("Prompts insertados/actualizados correctamente.")


if __name__ == "__main__":
    asyncio.run(main())
