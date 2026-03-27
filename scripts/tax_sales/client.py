from scripts.common.config import get_settings
from scripts.common.scraper_client import ScraperClient

settings = get_settings()


class TaxSalesClient(ScraperClient):
    def __init__(self):
        super().__init__(settings.URL_CT_TAX, False)
