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
    "field_goal_percentage": "field_goal_percentage",
    "three_point_percentage": "three_point_percentage",
    "free_throw_percentage": "free_throw_percentage",
    "minutes_played": "minutes_played"
}

MINIMUM_ATTEMPTS = {
    'field_goal_percentage': {"key": "field_goals_attempted", "threshold": 100},  # Minimum 100 FGA to qualify
    'free_throw_percentage': {"key": "free_throws_attempted", "threshold": 50},   # Minimum 50 FTA to qualify
    'three_point_percentage': {"key": "three_pointers_attempted", "threshold": 50}   # Minimum 50 3PA to qualify
}


@cors(origin="*")
def handler(event, context):
    print(event)
    try:
        query_params = event.get("queryStringParameters", {})
        category = query_params.get("category")
        season = query_params.get("season")
        team_name = query_params.get("teamName")
        stat_type = query_params.get("type", "average")

        if not category:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'category' query parameter."})
            }

        valid_categories = {"points", "rebounds", "assists", "blocks", "steals",
                            "field_goal_percentage", "three_point_percentage", "free_throw_percentage", "minutes_played"}
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
            players = [p for p in players if p.get(
                "teamName", "").lower() == team_name.lower()]

        if stat_type == "average" and category not in ["field_goal_percentage", "three_point_percentage", "free_throw_percentage",]:
            players = get_average_values(players, key_map.get(category))
        elif category in ["field_goal_percentage", "three_point_percentage", "free_throw_percentage"]:
            players = list(filter(lambda p: p.get(MINIMUM_ATTEMPTS[category]["key"]) >= MINIMUM_ATTEMPTS[category]["threshold"], players))
            players = get_percentage_values(players, key_map.get(category))

        # Sort players by the specified category
        if category == 'minutes_played':
            sorted_players = sorted(players,
                                    key=lambda p: minutes_to_seconds(
                                        p.get(key_map.get(category), '0:00')),
                                    reverse=True)
        else:
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


def minutes_to_seconds(minutes_str):
    if not minutes_str:
        return 0
    minutes, seconds = minutes_str.split(':')
    return int(minutes) * 60 + int(seconds)


def get_percentage_values(data, category_name):
    for inner_data in data:
        if category_name == "field_goal_percentage":
            field_goals_attempted = inner_data.get("field_goals_attempted") if inner_data.get("field_goals_attempted") > 0 else 1
            inner_data[category_name] = round(
                inner_data.get("field_goals_made", 0) / field_goals_attempted, 2)
        elif category_name == "three_point_percentage":
            three_pointers_attempted = inner_data.get("three_pointers_attempted") if inner_data.get("three_pointers_attempted") > 0 else 1
            inner_data[category_name] = round(
                inner_data.get("three_pointers_made", 0) / three_pointers_attempted, 2)
        elif category_name == "free_throw_percentage":
            free_throws_attempted = inner_data.get("free_throws_attempted") if inner_data.get("free_throws_attempted") > 0 else 1
            inner_data[category_name] = round(
                inner_data.get("free_throws_made", 0) / free_throws_attempted, 2)
    return data


def get_average_values(data, category_name):
    for inner_data in data:
        if category_name == "minutes_played":
            # Convert "MM:SS" format to average minutes per game
            minutes, seconds = inner_data[category_name].split(':')
            total_minutes = float(minutes) + float(seconds)/60
            avg_minutes = total_minutes / inner_data.get("game_count")
            # Format back to "MM:SS"
            avg_min = int(avg_minutes)
            avg_sec = int((avg_minutes - avg_min) * 60)
            inner_data[category_name] = f"{avg_min:02d}:{avg_sec:02d}"
        else:
            inner_data[category_name] = round(
                inner_data[category_name] / inner_data.get("game_count"), 2)
    return data


def prepare_result(data, category_name):
    result = []
    for inner in data:
        result.append({"player_name": inner.get("player_name"),
                       "team_name": inner.get("team_name"),
                       category_name: inner.get(category_name)
                       })
    return result
