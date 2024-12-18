from datetime import datetime, timedelta

from src.integrations.bdl import BallDontLie
from src.services.s3 import S3
from src.util.config import BDL_API_KEY, BUCKET_NAME

bdl = BallDontLie(BDL_API_KEY)
s3 = S3(BUCKET_NAME)


def handler(_event, _context):
    try:
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_iso_format = yesterday.strftime('%Y-%m-%d')
        games = bdl.get_games(date=yesterday_iso_format)
        s3.upload_to_bucket(data=games, key=f"{yesterday_iso_format}/bdl.json")
    except Exception as e:
        print(f"Error handling request: {str(e)}")
