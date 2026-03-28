import asyncio
import json
import logging
import os
import sys

from aws_python_helper import MongoManager
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.common.config import get_settings  # noqa: E402
from scripts.tax_sales.service import scrape_tax_sales  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

settings = get_settings()
MongoManager.initialize(settings.MONGO_URI)


async def main() -> None:
    await scrape_tax_sales()
    # results = await scrape_tax_sales()
    # print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
