import os
from dotenv import load_dotenv

load_dotenv()

BDL_API_KEY = os.getenv("BDL_API_KEY")
BUCKET_NAME =  os.getenv("BUCKET_NAME")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
GAME_TABLE_NAME = os.getenv("GAME_TABLE_NAME")
TEAM_TABLE_NAME = os.getenv("TEAM_TABLE_NAME")
NORMALIZE_GAME_QUEUE_URL = os.getenv("NORMALIZE_GAME_QUEUE_URL")
GAME_TABLE_INDEX = os.getenv("GAME_TABLE_INDEX")
TEAM_TABLE_NAME_INDEX = os.getenv("TEAM_TABLE_NAME_INDEX")