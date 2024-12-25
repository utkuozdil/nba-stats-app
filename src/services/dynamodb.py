import boto3
from boto3.dynamodb.conditions import Key
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

    def get_by_index_value(self, index_name, key, value, sort_key=None, sort_value=None):
        try:
            key_condition = Key(key).eq(value)
            if sort_key and sort_value:
                key_condition &= Key(sort_key).eq(sort_value)
            response = self.table.query(IndexName=index_name, KeyConditionExpression=key_condition)
            return response.get("Items", [])
        except Exception as e:
            print(f"Error querying by index: {key} {value} {str(e)}")
            raise

    def delete_batch(self, data):
        with self.table.batch_writer() as batch:
            for game in data:
                batch.delete_item(Key={"game_id": game.game_id, "date": game.date})

    def get_all_items(self, scan_params=None):
        try:
            items = []
            scan_params = scan_params or {}

            response = self.table.scan(**scan_params)
            items.extend(response.get("Items", []))
            return items
        except Exception as e:
            print(f"Error retrieving all items: {str(e)}")
            raise

