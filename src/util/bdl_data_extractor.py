import json

from src.model.game import Game
from src.model.team import Team


class BDLDataExtractor:

    def __init__(self, data):
        self.data = json.loads(data)

    def extract_game_data(self):
        data = self.data.get("data", [])

        extracted_games = []
        for game_data in data:
            home_team = self._get_team_data(game_data.get("home_team"))
            visitor_team = self._get_team_data(game_data.get("visitor_team"))
            game_id = self._generate_game_id(game_data)

            game = Game(
                home_team=home_team, visitor_team=visitor_team,
                home_team_score=game_data.get("home_team_score"),
                visitor_team_score=game_data.get("visitor_team_score"),
                postseason=game_data.get("postseason"),
                date=game_data.get("date"),
                season=game_data.get("season"),
                game_id=game_id,
                source="BallDontLie"
            )
            extracted_games.append(game)

        return extracted_games

    def _get_team_data(self, raw_team_data):
        team = Team(conference=raw_team_data.get("conference"),
                    division=raw_team_data.get("division"),
                    city=raw_team_data.get("city"),
                    name=raw_team_data.get("name"),
                    full_name=raw_team_data.get("full_name"),
                    abbreviation=raw_team_data.get("abbreviation")
                    )
        return team

    def _generate_game_id(self, game_data):
        date = game_data.get("date")
        home_team_abbr = game_data.get("home_team").get("abbreviation")
        visitor_team_abbr = game_data.get("visitor_team").get("abbreviation")
        return "_".join([date, home_team_abbr, visitor_team_abbr])
