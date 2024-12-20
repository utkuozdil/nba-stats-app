import json

import boto3


class SNS:

    def __init__(self, topic_arn: str):
        self.sns_client = boto3.client("sns")
        self.topic_arn = topic_arn

    def publish_to_topic(self, message, source):
        self.sns_client.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(message),
            MessageAttributes={
                "source": {
                    "DataType": "String",
                    "StringValue": source
                }
            }
        )
