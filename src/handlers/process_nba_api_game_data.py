import json

from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.util.config import BUCKET_NAME, GAME_TABLE_NAME
from src.util.nba_api_data_extractor import NBAAPIDataExtractor

s3 = S3(BUCKET_NAME)
dynamodb = DynamoDB(GAME_TABLE_NAME)


def handler(event, context):
    for record in event["Records"]:
        try:
            message_body = json.loads(record["body"])
            sqs_message = json.loads(message_body["Message"])
            s3_key = sqs_message["s3_key"]
            raw_data = s3.retrieve_data_from_bucket(key=s3_key)
            nba_api_data_extractor = NBAAPIDataExtractor(data=raw_data)
            extracted_games = nba_api_data_extractor.extract_game_data()
            dynamodb.save_batch(data=extracted_games)
        except Exception as e:
            print(f"Error processing message: {str(e)}")
