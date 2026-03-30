from aws_python_helper.api.base import API
from src.services.foreclosures_service import scrape_foreclosures


class ForeclosuresScrapePostAPI(API):
    async def process(self):
        result = await scrape_foreclosures()
        self.set_body(result)
