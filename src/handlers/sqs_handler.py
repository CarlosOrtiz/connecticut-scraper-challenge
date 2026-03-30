from aws_python_helper.sqs.handler import sqs_handler

execution_logs_consumer_handler = sqs_handler("execution-logs-consumer")

__all__ = ["execution_logs_consumer_handler"]
