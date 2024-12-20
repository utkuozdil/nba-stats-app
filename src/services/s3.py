import boto3


class S3:

    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_to_bucket(self, data, key):
        self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=data)

    def retrieve_data_from_bucket(self, key):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            return content
        except Exception as e:
            print(f"Error fetching object from S3: {str(e)}")
            return None