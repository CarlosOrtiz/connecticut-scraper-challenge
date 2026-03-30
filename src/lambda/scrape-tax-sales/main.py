from datetime import datetime, timezone

from aws_python_helper.lambda_standalone.base import Lambda

from src.services.tax_sales_service import scrape_tax_sales
from src.topic.tax_sales_finished import TaxSalesFinishedTopic


class ScrapeTaxSalesLambda(Lambda):
    async def process(self):
        started_at = datetime.now(timezone.utc).isoformat()
        status = "success"
        error_message = None
        records_processed = 0

        try:
            result = await scrape_tax_sales()
            records_processed = len(result)
        except Exception as exc:
            self.logger.exception("Error running scrape-tax-sales")
            status = "error"
            error_message = str(exc)
            result = []

        finished_at = datetime.now(timezone.utc).isoformat()

        message = {
            "process_name": "scrape-tax-sales",
            "started_at": started_at,
            "finished_at": finished_at,
            "records_processed": records_processed,
            "status": status,
            "error_message": error_message,
        }

        TaxSalesFinishedTopic().publish(message)

        return message
