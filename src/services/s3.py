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

    def list_files(self):
        file_names = []

        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            operation_parameters = {'Bucket': self.bucket_name}

            for page in paginator.paginate(**operation_parameters):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_names.append(obj['Key'])

            return file_names

        except Exception as e:
            print(f"Error retrieving files: {e}")
            return []
