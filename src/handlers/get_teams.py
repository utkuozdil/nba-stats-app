import json
from src.services.dynamodb import DynamoDB
from src.util.config import TEAM_TABLE_NAME, TEAM_TABLE_CONFERENCE_INDEX, TEAM_TABLE_DIVISION_INDEX, \
    TEAM_TABLE_NAME_INDEX
from src.util.process_data_util import convert_decimals

dynamodb = DynamoDB(TEAM_TABLE_NAME)


def handler(event, context):
    print(event)
    try:
        query_params = event.get("queryStringParameters", {})
        season = query_params.get("season")
        conference = query_params.get("conference")
        division = query_params.get("division")
        team_name = query_params.get("team_name")

        if not season:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'season' query parameter."})
            }

        filters = [conference, division, team_name]
        if sum(1 for f in filters if f) != 1:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Provide exactly one of 'conference', 'division', or 'team_name' as a filter."
                })
            }

        if conference:
            key = "conference"
            value = conference
            index_name = TEAM_TABLE_CONFERENCE_INDEX
        elif division:
            key = "division"
            value = division
            index_name = TEAM_TABLE_DIVISION_INDEX
        elif team_name:
            key = "team_name"
            value = team_name
            index_name = TEAM_TABLE_NAME_INDEX
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid filter parameters."})
            }

        teams = dynamodb.get_by_index_value(index_name=index_name, key=key, value=value, sort_key="season",
                                            sort_value=int(season))
        results = convert_decimals(teams)

        return {
            "statusCode": 200,
            "body": json.dumps(results)
        }

    except Exception as e:
        print(f"Error fetching teams: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }