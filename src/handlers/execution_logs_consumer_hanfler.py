import asyncio
import logging

from src.services.execution_logs_consumer import consume_execution_log

logger = logging.getLogger(__name__)


def handler(event, context):
    records = event.get("Records", [])

    for record in records:
        asyncio.run(consume_execution_log(record))

    return {"processed_messages": len(records)}
