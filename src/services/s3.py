import boto3


class S3:

    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_to_bucket(self, data, key):
        self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=data)