from aws_python_helper.sns.publisher import SNSPublisher

from src.common.config import get_settings


class TaxSalesFinishedTopic(SNSPublisher):
    def __init__(self):
        settings = get_settings()
        super().__init__(topic_arn=settings.SNS_TOPIC_ARN)

    def publish_execution_finished(self, message: dict):
        self.publish(message=message, subject="tax-sales-execution-finished")
