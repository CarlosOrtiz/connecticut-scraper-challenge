import asyncio
import json
import logging
from datetime import datetime, timezone

import boto3

from scripts.tax_sales.service import scrape_tax_sales

logger = logging.getLogger(__name__)
sns = boto3.client("sns")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:tax-sales-finished"


def handler(event, context):
    started_at = datetime.now(timezone.utc).isoformat()
    status = "success"
    error_message = None
    records_processed = 0

    logger.info("Running standalone lambda: scrape-tax-sales")

    try:
        result = asyncio.run(scrape_tax_sales())
        records_processed = len(result)
    except Exception as exc:
        logger.exception("Error running scrape-tax-sales")
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

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        Subject="tax-sales-execution-finished",
    )

    return message
