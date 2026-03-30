import json
from aws_python_helper.sqs.consumer_base import SQSConsumer
from src.services.execution_logs_consumer import create_execution_log


class ExecutionLogsConsumer(SQSConsumer):
    async def process_record(self, record):
        body = self.parse_body(record)
        message = json.loads(body["Message"])
        await create_execution_log(message)
