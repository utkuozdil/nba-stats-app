import json
from src.services.dynamodb import DynamoDB
from src.util.config import GAME_TABLE_NAME, GAME_TABLE_INDEX
from src.util.process_data_util import convert_decimals

dynamodb = DynamoDB(GAME_TABLE_NAME)


def handler(event, context):
    try:
        query_params = event.get("queryStringParameters", {})
        date = query_params.get("date")

        if not date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'date' query parameter."})
            }

        games = dynamodb.get_by_index_value(index_name=GAME_TABLE_INDEX, key="date", date=date)
        results = prepare_results(convert_decimals(games))
        return {
            "statusCode": 200,
            "body": json.dumps(results)
        }

    except Exception as e:
        print(f"Error fetching games: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }


def prepare_results(data):
    results = []
    for game in data:
        game_map = {game["home_team"]["full_name"]: game["home_team_score"],
                    game["visitor_team"]["full_name"]: game["visitor_team_score"]}
        results.append(game_map)
    return {"games": results}

