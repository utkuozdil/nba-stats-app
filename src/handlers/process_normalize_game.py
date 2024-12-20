import json
import traceback

from src.services.dynamodb import DynamoDB
from src.util.config import GAME_TABLE_NAME
dynamodb = DynamoDB(GAME_TABLE_NAME)

def handler(event, context):
    for record in event["Records"]:
        try:
            message_body = json.loads(record["body"])
            message_body.split("#")
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing message: {str(e)}")
