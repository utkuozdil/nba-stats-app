import boto3
from botocore.exceptions import ClientError


class DynamoDB:

    def __init__(self, table_name: str):
        self.dynamodb_client = boto3.resource("dynamodb")
        self.table = self.dynamodb_client.Table(table_name)

    def save_batch(self, data):
        with self.table.batch_writer() as batch:
            for game in data:
                batch.put_item(Item=game.dict())

    def get_item(self, key: dict):
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item", None)
        except ClientError as e:
            print(f"Error retrieving item: {str(e)}")
            raise

    def delete_batch(self, data):
        with self.table.batch_writer() as batch:
            for game in data:
                batch.delete_item(Key={"game_id": game.game_id, "date": game.date})