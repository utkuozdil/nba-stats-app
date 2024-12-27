import json
import traceback

from src.services.aws.dynamodb import DynamoDB
from src.services.aws.s3 import S3
from src.utility.util.config import BUCKET_NAME, GAME_TABLE_NAME, GAME_TABLE_INDEX
from src.utility.extractor.nba_api_game_data_extractor import NBAAPIDataExtractor
from src.utility.util.process_data_util import filter_games

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
            if len(extracted_games) > 0:
                dynamodb.save_batch(data=extracted_games)
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")

