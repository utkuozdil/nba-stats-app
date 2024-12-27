from src.integrations.nbacom import NbaCom
from src.services.aws.s3 import S3
from src.services.aws.sns import SNS
from src.utility.util.config import BUCKET_NAME, SNS_TOPIC_ARN
from src.utility.util.date_util import get_yesterday_date_str

nbaAPI = NbaCom()
s3 = S3(BUCKET_NAME)
sns = SNS(SNS_TOPIC_ARN)


def handler(_event, _context):
    try:
        yesterday_iso_format = get_yesterday_date_str()
        games = nbaAPI.get_games(date=yesterday_iso_format)
        s3.upload_to_bucket(data=games, key=f"{yesterday_iso_format}/nba-api.json")
        sns_message = {
            "source": "NBA_API",
            "date": yesterday_iso_format,
            "s3_key": f"{yesterday_iso_format}/nba-api.json"
        }
        sns.publish_to_topic(message=sns_message, source="NBA_API")
    except Exception as e:
        print(f"Error handling request: {str(e)}")