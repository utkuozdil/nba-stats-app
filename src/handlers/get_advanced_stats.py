import json
import traceback

from src.services.aws.dynamodb import DynamoDB
from src.utility.util.config import PLAYER_ADVANCED_TABLE_NAME
from src.utility.decorator.cors_decorator import cors
from src.utility.util.process_data_util import convert_decimals

dynamodb = DynamoDB(PLAYER_ADVANCED_TABLE_NAME)

key_map = {
    "ts_percentage": "ts_percentage",
    "efg_percentage": "efg_percentage",
    "usage_rate": "usage_rate",
    "off_rating": "off_rating",
    "def_rating": "def_rating",
    "net_rating": "net_rating"
}

MINIMUM_ATTEMPTS = {
    "ts_percentage": {"key": "total_attempts", "threshold": 200},
    "efg_percentage": {"key": "total_attempts", "threshold": 200},
    "usage_rate": {"key": "total_attempts", "threshold": 200},
    "off_rating": {"key": "total_attempts", "threshold": 200},
    "def_rating": {"key": "total_attempts", "threshold": 200},
    "net_rating": {"key": "total_attempts", "threshold": 200}
}


@cors(origin="*")
def handler(event, context):
    print(event)
    try:
        query_params = event.get("queryStringParameters", {})
        category = query_params.get("category")
        season = query_params.get("season")
        team_name = query_params.get("teamName")

        if not category:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'category' query parameter."})
            }

        valid_categories = {"ts_percentage", "efg_percentage",
                            "usage_rate", "off_rating", "def_rating", "net_rating"}
        if category not in valid_categories:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid 'category'. Must be one of {list(valid_categories)}."})
            }

        # Validate season
        if season:
            try:
                season = int(season)
                if season < 2000 or season > 2100:  # reasonable range
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Invalid season value"})
                    }
            except ValueError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Season must be a valid year"})
                }

        # Fetch players
        players = dynamodb.get_all_items(scan_params={})
        players = convert_decimals(players)

        players = list(filter(lambda p: p.get(
            MINIMUM_ATTEMPTS[category]["key"]) >= MINIMUM_ATTEMPTS[category]["threshold"], players))

        # Filter by season if provided
        if season:
            players = [p for p in players if p.get("season") == int(season)]

        # Filter by teamName if provided
        if team_name:
            players = [p for p in players if p.get(
                "team_name", "").lower() == team_name.lower()]

        players = prepare_data(players)

        sorted_players = sorted(players, key=lambda p: p.get(
            key_map.get(category), 0), reverse=True)

        top_players = prepare_result(sorted_players, key_map.get(category))

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


def prepare_data(data):
    for inner_data in data:
        inner_data["ts_percentage"] = inner_data.get("ts_percentage", 0) * 100
        inner_data["efg_percentage"] = inner_data.get(
            "efg_percentage", 0) * 100
        inner_data["usage_rate"] = inner_data.get("usage_rate", 0) * 100

        inner_data["off_rating"] = inner_data.get(
            "off_rating", 0) / len(inner_data.get("game_ids", []))
        inner_data["def_rating"] = inner_data.get(
            "def_rating", 0) / len(inner_data.get("game_ids", []))
        inner_data["net_rating"] = inner_data.get(
            "net_rating", 0) / len(inner_data.get("game_ids", []))
    return data


def prepare_result(data, category_name):
    result = []
    for inner in data:  # Limit to top 10 players
        result.append({
            "player_name": inner.get("player_name"),
            "team_name": inner.get("team_name"),
            # Round to 2 decimal places
            "value": round(inner.get(category_name, 0), 2)
        })
    return result
