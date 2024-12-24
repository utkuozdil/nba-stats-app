import json
import traceback

from src.services.dynamodb import DynamoDB
from src.util.config import PLAYER_TABLE_NAME
from src.util.cors_decorator import cors
from src.util.process_data_util import convert_decimals

dynamodb = DynamoDB(PLAYER_TABLE_NAME)

key_map = {
    "points": "point_count",
    "rebounds": "total_rebound",
    "assists": "assist_count",
    "blocks": "block_count",
    "steals": "steal_count",
}

@cors(origin="*")
def handler(event, context):
    print(event)
    try:
        query_params = event.get("queryStringParameters", {})
        category = query_params.get("category")
        season = query_params.get("season")
        team_name = query_params.get("teamName")
        limit = int(query_params.get("limit", 10))
        stat_type = query_params.get("type", "average")

        if not category:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'category' query parameter."})
            }

        valid_categories = {"points", "rebounds", "assists", "blocks", "steals"}
        if category not in valid_categories:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid 'category'. Must be one of {list(valid_categories)}."})
            }

        # Fetch players
        players = dynamodb.get_all_items(scan_params={})
        players = convert_decimals(players)

        # Filter by season if provided
        if season:
            players = [p for p in players if p.get("season") == int(season)]

        # Filter by teamName if provided
        if team_name:
            players = [p for p in players if p.get("teamName", "").lower() == team_name.lower()]

        if stat_type == "average":
            players = get_average_values(players, key_map.get(category))

        # Sort players by the specified category
        sorted_players = sorted(players, key=lambda p: p.get(key_map.get(category), 0), reverse=True)

        # Apply limit
        top_players = sorted_players[:limit]

        top_players = prepare_result(top_players, key_map.get(category))

        # Prepare response
        response_body = {"leaders": top_players}
        return {
            "statusCode": 200,
            "body": json.dumps(response_body, ensure_ascii=False)
        }

    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching leaders: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }


def get_average_values(data, category_name):
    for inner_data in data:
        inner_data[category_name] = round(inner_data[category_name] / inner_data.get("game_count"), 2)
    return data


def prepare_result(data, category_name):
    result = []
    for inner in data:
        result.append({"player_name": inner.get("player_name"),
                       "team_name": inner.get("team_name"),
                       category_name: inner.get(category_name)
                       })
    return result
