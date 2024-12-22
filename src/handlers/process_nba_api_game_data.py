import json
import traceback

from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.services.sqs import SQS
from src.util.config import BUCKET_NAME, GAME_TABLE_NAME, NORMALIZE_GAME_QUEUE_URL, GAME_TABLE_INDEX
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
            if len(extracted_games) > 0:
                date = extracted_games[0].date
                previously_recorded_games = dynamodb.get_by_date(index_name=GAME_TABLE_INDEX,
                                                                 key="date", date=date)
                prev_recorded_unified_games = list(
                    filter(lambda x: x["source"] == "Unified", previously_recorded_games))
                prev_recorded_unified_game_ids = set([x["game_id"]
                                                      for x in prev_recorded_unified_games])

                filtered_games = []
                for extracted_game in extracted_games:
                    temp_game_id = "_".join([extracted_game.date,
                                        extracted_game.home_team.abbreviation,
                                        extracted_game.visitor_team.abbreviation,
                                        "Unified"])
                    if temp_game_id not in prev_recorded_unified_game_ids:
                        filtered_games.append(extracted_game)

                dynamodb.save_batch(data=filtered_games)
                for extracted_game in filtered_games:
                    game_id = "_".join([extracted_game.date,
                                        extracted_game.home_team.abbreviation,
                                        extracted_game.visitor_team.abbreviation,
                                        "NBA_API"
                                        ])
                    sqs.send_message(message=game_id)
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")
