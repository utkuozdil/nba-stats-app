import json

from nba_api.stats.endpoints import scoreboardv2


class NbaCom:

    def __init__(self):
        self.scoreboardAPI = scoreboardv2

    def get_games(self, date: str):
        games = self.scoreboardAPI.ScoreboardV2(game_date=date)
        raw_json = games.get_json()
        return raw_json
