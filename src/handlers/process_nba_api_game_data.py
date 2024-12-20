import json
import traceback

from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.services.sqs import SQS
from src.util.config import BUCKET_NAME, GAME_TABLE_NAME, NORMALIZE_GAME_QUEUE_URL
from src.util.date_util import get_yesterday_date_str
from src.util.nba_api_data_extractor import NBAAPIDataExtractor

s3 = S3(BUCKET_NAME)
dynamodb = DynamoDB(GAME_TABLE_NAME)
sqs = SQS(NORMALIZE_GAME_QUEUE_URL)

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
            yesterday_date_str = get_yesterday_date_str()
            for extracted_game in extracted_games:
                game_id = "_".join([yesterday_date_str,
                                    extracted_game.home_team.abbreviation,
                                    extracted_game.visitor_team.abbreviation,
                                    "NBA_API"
                                    ])
                sqs.send_message(message=game_id)
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")
