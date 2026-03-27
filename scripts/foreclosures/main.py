import asyncio
import os
import sys

from aws_python_helper import MongoManager
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main() -> None:
    load_dotenv()
    from scripts.common.config import get_settings
    from scripts.foreclosures.service import scrape_foreclosures

    settings = get_settings()
    MongoManager.initialize(settings.MONGO_URI)
    asyncio.run(scrape_foreclosures())


if __name__ == "__main__":
    main()
