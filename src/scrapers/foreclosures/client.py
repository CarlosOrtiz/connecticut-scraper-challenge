from src.common.config import get_settings
from src.common.scraper_client import ScraperClient

settings = get_settings()


class ForeclosuresClient(ScraperClient):
    def __init__(self):
        super().__init__(settings.BASE_URL_CT, True)

    @property
    def index_url(self):
        return f"{self.base_url}PendPostbyTownList.aspx"
