from balldontlie import BalldontlieAPI


class BallDontLie:

    def __init__(self, api_key: str):
        self.api = BalldontlieAPI(api_key=api_key)

    def get_games(self, date: str):
        games = self.api.nba.games.list(dates=[date], per_page=100)
        return games.model_dump_json(indent=2)