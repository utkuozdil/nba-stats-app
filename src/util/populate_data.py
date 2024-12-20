import time
from datetime import datetime, timedelta

from src.integrations.bdl import BallDontLie
from src.integrations.nbacom import NbaCom
from src.services.s3 import S3
from src.services.sns import SNS
from src.util.config import BDL_API_KEY, BUCKET_NAME, SNS_TOPIC_ARN


def populate_bdl_data(query_date, end_date):
    bdl = BallDontLie(BDL_API_KEY)
    s3 = S3(BUCKET_NAME)
    sns = SNS(SNS_TOPIC_ARN)

    while query_date != end_date:
        games = bdl.get_games(date=query_date)
        s3.upload_to_bucket(data=games, key=f"{query_date}/bdl.json")

        print(f"{query_date} is added for BDL")
        query_date = datetime.strptime(query_date, '%Y-%m-%d') + timedelta(days=1)
        query_date = query_date.strftime('%Y-%m-%d')
        time.sleep(6)

def populate_nba_api_data(query_date, end_date):
    nbaAPI = NbaCom()
    s3 = S3(BUCKET_NAME)

    while query_date != end_date:
        games = nbaAPI.get_games(date=query_date)
        s3.upload_to_bucket(data=games, key=f"{query_date}/nba-api.json")
        sns_message = {
            "source": "NBA_API",
            "date": query_date,
            "s3_key": f"{query_date}/nba-api.json"
        }
        sns.publish_to_topic(message=sns_message, source="NBA_API")
        print(f"{query_date} is added for NBA API")
        query_date = datetime.strptime(query_date, '%Y-%m-%d') + timedelta(days=1)
        query_date = query_date.strftime('%Y-%m-%d')
        time.sleep(1)


populate_bdl_data("2024-10-22", "2024-12-18")
populate_nba_api_data("2024-10-22", "2024-12-18")
