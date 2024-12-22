import time
from datetime import datetime, timedelta

from src.integrations.bdl import BallDontLie
from src.integrations.nbacom import NbaCom
from src.services.s3 import S3
from src.services.sns import SNS
from src.util.config import BDL_API_KEY, BUCKET_NAME, SNS_TOPIC_ARN

s3 = S3(BUCKET_NAME)
sns = SNS(SNS_TOPIC_ARN)
bdl = BallDontLie(BDL_API_KEY)
nbaAPI = NbaCom()

start_date = "2024-10-22"
end_date = "2024-12-22"

def populate_bdl_data(query_date, end_date_param, file_set):
    while query_date != end_date_param:
        key = f"{query_date}/bdl.json"

        if key not in file_set:
            games = bdl.get_games(date=query_date)
            s3.upload_to_bucket(data=games, key=key)
            sns_message = {
                "source": "BallDontLie",
                "date": query_date,
                "s3_key": key
            }
            sns.publish_to_topic(message=sns_message, source="BallDontLie")
            print(f"{query_date} is added for BDL")
            time.sleep(6)
        else:
            print(f"{query_date} is already added for BDL")
            # sns_message = {
            #     "source": "BallDontLie",
            #     "date": query_date,
            #     "s3_key": key
            # }
            # sns.publish_to_topic(message=sns_message, source="BallDontLie")

        query_date = datetime.strptime(query_date, '%Y-%m-%d') + timedelta(days=1)
        query_date = query_date.strftime('%Y-%m-%d')


def populate_nba_api_data(query_date, end_date_param, file_set):
    while query_date != end_date_param:
        key = f"{query_date}/nba-api.json"

        if key not in file_set:
            games = nbaAPI.get_games(date=query_date)
            s3.upload_to_bucket(data=games, key=key)
            sns_message = {
                "source": "NBA_API",
                "date": query_date,
                "s3_key": key
            }
            sns.publish_to_topic(message=sns_message, source="NBA_API")
            print(f"{query_date} is added for NBA API")
            time.sleep(1)
        else:
            print(f"{query_date} is already added for NBA API")
            # sns_message = {
            #     "source": "NBA_API",
            #     "date": query_date,
            #     "s3_key": key
            # }
            # sns.publish_to_topic(message=sns_message, source="NBA_API")

        query_date = datetime.strptime(query_date, '%Y-%m-%d') + timedelta(days=1)
        query_date = query_date.strftime('%Y-%m-%d')


def populate_data(start_date_param, end_date_param):
    all_files = set(s3.list_files())
    populate_bdl_data(start_date_param, end_date_param, all_files)
    populate_nba_api_data(start_date_param, end_date_param, all_files)


populate_data(start_date_param=start_date, end_date_param=end_date)
