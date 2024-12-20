import boto3


class DynamoDB:

    def __init__(self, table_name: str):
        self.dynamodb_client = boto3.resource("dynamodb")
        self.table = self.dynamodb_client.Table(table_name)

    def save_batch(self, data):
        with self.table.batch_writer() as batch:
            for game in data:
                batch.put_item(Item=game.dict())