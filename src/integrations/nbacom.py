from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv3


class NbaCom:

    def __init__(self):
        self.scoreboardAPI = scoreboardv2
        self.boxscoreAPI = boxscoretraditionalv3

    def get_games(self, date: str):
        games = self.scoreboardAPI.ScoreboardV2(game_date=date)
        raw_json = games.get_json()
        return raw_json

    def get_box_score_for_games(self, game_id):
        box_score = self.boxscoreAPI.BoxScoreTraditionalV3(game_id=game_id)
        raw_json = box_score.get_json()
        return raw_json
