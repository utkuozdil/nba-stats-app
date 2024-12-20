import os
from dotenv import load_dotenv

load_dotenv()

BDL_API_KEY = os.getenv("BDL_API_KEY")
BUCKET_NAME =  os.getenv("BUCKET_NAME")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")