from datetime import datetime, timedelta

from src.integrations.nbacom import NbaCom
from src.services.s3 import S3
from src.services.sns import SNS
from src.util.config import BUCKET_NAME, SNS_TOPIC_ARN

nbaAPI = NbaCom()
s3 = S3(BUCKET_NAME)
sns = SNS(SNS_TOPIC_ARN)


def handler(_event, _context):
    try:
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_iso_format = yesterday.strftime('%Y-%m-%d')
        games = nbaAPI.get_games(date=yesterday_iso_format)
        s3.upload_to_bucket(data=games, key=f"{yesterday_iso_format}/nba-api.json")
        sns_message = {
            "source": "NBA_API",
            "date": yesterday_iso_format,
            "s3_key": f"{yesterday_iso_format}/bdl.json"
        }
        sns.publish_to_topic(message=sns_message, source="NBA_API")
    except Exception as e:
        print(f"Error handling request: {str(e)}")
