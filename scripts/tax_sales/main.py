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

from scripts.common.config import get_settings
from scripts.tax_sales.service import scrape_tax_sales

settings = get_settings()
MongoManager.initialize(settings.MONGO_URI)

logger = logging.getLogger(__name__)


def main() -> None:
    results = scrape_tax_sales()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
