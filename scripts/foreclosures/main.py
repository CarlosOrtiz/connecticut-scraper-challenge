import asyncio
import json
import os
import sys

from aws_python_helper import MongoManager
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.common.config import get_settings  # noqa: E402
from src.common.logging_config import setup_logging  # noqa: E402
from src.services.foreclosures_service import scrape_foreclosures  # noqa: E402

setup_logging()
settings = get_settings()
MongoManager.initialize(settings.MONGO_URI)


async def main() -> None:
    results = await scrape_foreclosures()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
