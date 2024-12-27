from datetime import datetime, timedelta


def get_yesterday_date_str():
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_iso_format = yesterday.strftime('%Y-%m-%d')
    return yesterday_iso_format