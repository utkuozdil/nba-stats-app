import json
from src.services.dynamodb import DynamoDB
from src.util.config import GAME_TABLE_NAME

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

        index_name = "GameDateIndex"  # Replace with your actual GSI name
        games = dynamodb.get_by_date(index_name=index_name, key="date", date=date)

        return {
            "statusCode": 200,
            "body": json.dumps(games)
        }

    except Exception as e:
        print(f"Error fetching games: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
