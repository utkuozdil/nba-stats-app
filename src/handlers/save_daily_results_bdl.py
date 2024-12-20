from datetime import datetime, timedelta

from src.integrations.bdl import BallDontLie
from src.services.s3 import S3
from src.services.sns import SNS
from src.util.config import BDL_API_KEY, BUCKET_NAME, SNS_TOPIC_ARN
from src.util.date_util import get_yesterday_date_str

bdl = BallDontLie(BDL_API_KEY)
s3 = S3(BUCKET_NAME)
sns = SNS(SNS_TOPIC_ARN)

def handler(_event, _context):
    try:
        yesterday_iso_format = get_yesterday_date_str()
        games = bdl.get_games(date=yesterday_iso_format)
        s3.upload_to_bucket(data=games, key=f"{yesterday_iso_format}/bdl.json")
        sns_message = {
            "source": "BallDontLie",
            "date": yesterday_iso_format,
            "s3_key": f"{yesterday_iso_format}/bdl.json"
        }
        sns.publish_to_topic(message=sns_message, source="BallDontLie")
    except Exception as e:
        print(f"Error handling request: {str(e)}")
