import json
import traceback

from src.model.game import Game
from src.services.dynamodb import DynamoDB
from src.util.config import GAME_TABLE_NAME

dynamodb = DynamoDB(GAME_TABLE_NAME)


def get_other_key(key):
    array = key.split("_")
    if array[-1] == "BallDontLie":
        array[-1] = "NBA_API"
        return "_".join(array)
    else:
        array[-1] = "BallDontLie"
        return "_".join(array)


def compare_items(given_item: Game, other_item: Game):
    exclude_data_set = set()
    exclude_data_set.add("game_id")
    exclude_data_set.add("source")
    dict1 = given_item.model_dump(exclude=exclude_data_set)
    dict2 = other_item.model_dump(exclude=exclude_data_set)
    return dict1 == dict2


def handler(event, context):
    for record in event["Records"]:
        try:
            key = json.loads(record["body"])
            other_key = get_other_key(key)
            other_item = dynamodb.get_item({"game_id": other_key})
            if other_item:
                given_item = dynamodb.get_item({"game_id": key})
                is_equal = compare_items(given_item, other_item)
                if is_equal:
                    dynamodb.delete_item({"game_id": key})
                    dynamodb.delete_item({"game_id": other_key})
                    given_item.source = "Unified"
                    given_item.game_id = "_".join([given_item.date,
                                                   given_item.home_team.abbreviation,
                                                   given_item.visitor_team.abbreviation,
                                                   "Unified"])
                    dynamodb.save_batch([given_item])
                else:
                    raise Exception(f"Data mismatch for game_id: {key}.")

        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")
