from datetime import datetime, timedelta
import time
from src.integrations.nbacom import NbaCom
from src.services.aws.s3 import S3
from src.services.aws.sns import SNS
from src.utility.util.config import BUCKET_NAME, SNS_TOPIC_ARN


class GameAndTeamPopulator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.s3 = S3(BUCKET_NAME)
        self.s3_data = set(self.s3.list_files())
        self.nbaAPI = NbaCom()
        self.sns = SNS(SNS_TOPIC_ARN)
        
    def populate_data(self):
        while self.start_date != self.end_date:
            key = f"{self.start_date}/nba-api.json"

            if key not in self.s3_data:
                games = self.nbaAPI.get_games(date=self.start_date)
                self.s3.upload_to_bucket(data=games, key=key)
                sns_message = {
                    "source": "NBA_API",
                    "date": self.start_date,
                    "s3_key": key
                }
                self.sns.publish_to_topic(message=sns_message, source="NBA_API")
                print(f"{self.start_date} is added for NBA API")
                time.sleep(1)
            else:
                print(f"{self.start_date} is already added for NBA API")

            self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d') + timedelta(days=1)
            self.start_date = self.start_date.strftime('%Y-%m-%d')
