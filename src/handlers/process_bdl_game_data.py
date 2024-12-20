import json

from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.util.bdl_data_extractor import BDLDataExtractor
from src.util.config import BUCKET_NAME, GAME_TABLE_NAME

s3 = S3(BUCKET_NAME)
dynamodb = DynamoDB(GAME_TABLE_NAME)

def handler(event, context):
    for record in event["Records"]:
        try:
            message_body = json.loads(record["body"])
            sqs_message = json.loads(message_body["Message"])
            s3_key = sqs_message["s3_key"]
            raw_data = s3.retrieve_data_from_bucket(key=s3_key)
            bdl_data_extractor = BDLDataExtractor(data=raw_data)
            extracted_games = bdl_data_extractor.extract_game_data()
            dynamodb.save_batch(data=extracted_games)
        except Exception as e:
            print(f"Error processing message: {str(e)}")



e = {'Records': [{'messageId': '67c19156-554f-49b6-89c7-f397a702a87d', 'receiptHandle': 'AQEB+fBWD/1E8RurB6PuZ57A3DSqiVyhb11DKad72WJYNQdqhktEGQpGDAlXwSZcCoi5vup7SdRtlrw369ViS9MTCZDKGKhKYZRq/Vuv43e+KDKPp4PrrM0NbQyVQWY7f1BCO0ZrcKsYfGsYtdTGoIXgEp1Ue55VgjrhRR1Ez4UxkqP5GvxEkNzYRW9P8kLTa7pQCj93muv/bMZnH196nlWher/RD0UpPdkeofF/2bVKzuXKPD1brc56xeVAhffKyN5g8w3pfetsyU35SGOVW0BiSH/xmVpp8LuQujU7BVM7r2ngiR43J/qp9yf8rvWMpyyF6ENeP8dnGh3tH9UkQFv2h6YhQVwQrWJ/6nCXY05yOySXB6GWvqteUs1D5tmF9K4Z2ehxMvxWEQS9x69QBjgc0g==', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "6fd5d0ec-1613-5c60-a78c-8f332c9b8445",\n  "TopicArn" : "arn:aws:sns:us-east-1:795366345505:FanoutTopic",\n  "Message" : "{\\"source\\": \\"BallDontLie\\", \\"date\\": \\"2024-12-19\\", \\"s3_key\\": \\"2024-12-19/bdl.json\\"}",\n  "Timestamp" : "2024-12-20T09:26:32.529Z",\n  "SignatureVersion" : "1",\n  "Signature" : "FYSYWgwtCUC5qpIzH1LPCsHCwSQwieKLoNDZ75jVJVaZxwRm3OBQL1eNrO1K9sajQa8p2+Ou99TPBw81GHa2PVPaAXQ2i+5diucFLvt7K7FWfO1VPCkiohY8iVzScqnZKp68fqpnvW11IGhngVAx3K9n6jUjpJWel8JGZ3/UIPYlUaJYKAzV1uUV360dLB9GHtncvhJJ04itJ8cWSOMScjO3/N68D1JXs01Ff7aou9Ab/sTHP6ey2MzDDMIu4iyTO+IFb99+xQH16TVVgep22IrTTMs7wafRhCXJNl7QPfQWWkTgnrY7w3PZegEpMVhv19M4JXEaBRpe9mPdDGJzig==",\n  "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-9c6465fa7f48f5cacd23014631ec1136.pem",\n  "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:795366345505:FanoutTopic:93cd839f-11b0-47b6-83e6-cf496c48b1b9",\n  "MessageAttributes" : {\n    "source" : {"Type":"String","Value":"BallDontLie"}\n  }\n}', 'attributes': {'ApproximateReceiveCount': '1', 'AWSTraceHeader': 'Root=1-67653844-777661456c06580432b78cac;Parent=33520723e9d85b5f;Sampled=0;Lineage=1:5b4cd4a8:0', 'SentTimestamp': '1734686792569', 'SenderId': 'AIDAIT2UOQQY3AUEKVGXU', 'ApproximateFirstReceiveTimestamp': '1734688084503'}, 'messageAttributes': {}, 'md5OfBody': '9117a395397b37b588398a1d1beb0d37', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-east-1:795366345505:BDLGameQueue', 'awsRegion': 'us-east-1'}]}
handler(e, {})