import json
import traceback

from src.model.game import Game
from src.services.dynamodb import DynamoDB
from src.util.config import GAME_TABLE_NAME

dynamodb = DynamoDB(GAME_TABLE_NAME)


def get_other_key(key):
    if "BallDontLie" in key:
        return key.replace("BallDontLie", "NBA_API")
    else:
        return key.replace("NBA_API", "BallDontLie")


def compare_items(given_item: Game, other_item: Game):
    exclude_data_set = set()
    exclude_data_set.add("game_id")
    exclude_data_set.add("source")
    dict1 = given_item.model_dump(exclude=exclude_data_set)
    dict2 = other_item.model_dump(exclude=exclude_data_set)
    return dict1 == dict2


def handler(event, context):
    print(event)
    for record in event["Records"]:
        try:
            key = json.loads(record["body"])
            array = key.split("_")
            date = array[0]

            other_key = get_other_key(key)
            other_item = dynamodb.get_item({"game_id": other_key, "date": date})
            if other_item:
                given_item = dynamodb.get_item({"game_id": key, "date": date})

                other_item = Game.model_validate(other_item)
                given_item = Game.model_validate(given_item)

                is_equal = compare_items(given_item, other_item)
                if is_equal:
                    new_item = given_item.model_copy(deep=True)
                    dynamodb.delete_batch([given_item, other_item])
                    new_item.source = "Unified"
                    new_item.game_id = "_".join([new_item.date,
                                                 new_item.home_team.abbreviation,
                                                 new_item.visitor_team.abbreviation,
                                                 "Unified"])
                    dynamodb.save_batch([new_item])
                else:
                    raise Exception(f"Data mismatch for game_id: {key}.")

        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")
