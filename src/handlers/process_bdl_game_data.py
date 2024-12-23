import json

from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.services.sqs import SQS
from src.util.bdl_data_extractor import BDLDataExtractor
from src.util.config import BUCKET_NAME, GAME_TABLE_NAME, NORMALIZE_GAME_QUEUE_URL, GAME_TABLE_INDEX
from src.util.process_data_util import filter_games, generate_game_id

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
            bdl_data_extractor = BDLDataExtractor(data=raw_data)
            extracted_games = bdl_data_extractor.extract_game_data()
            if len(extracted_games) > 0:
                date = extracted_games[0].date
                previously_recorded_games = dynamodb.get_by_index_value(index_name=GAME_TABLE_INDEX,
                                                                        key="date", value=date)
                filtered_games = filter_games(extracted_games, previously_recorded_games)
                dynamodb.save_batch(data=filtered_games)
                for extracted_game in filtered_games:
                    game_id = generate_game_id(extracted_game, "BallDontLie")
                    sqs.send_message(message=game_id)
        except Exception as e:
            print(f"Error processing message: {str(e)}")
