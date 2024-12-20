import json
import boto3


class SQS:

    def __init__(self, queue_url: str):
        self.sqs_client = boto3.client("sqs")
        self.queue_url = queue_url

    def send_message(self, message):
        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message)
        )
