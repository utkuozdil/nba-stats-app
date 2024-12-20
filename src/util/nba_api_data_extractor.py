import json
from datetime import datetime

from src.model.game import Game
from src.model.team import Team
from src.util.constant import nba_divisions


class NBAAPIDataExtractor:

    def __init__(self, data):
        self.data = json.loads(data)

    def extract_game_data(self):
        extracted_games = []
        game_header = None
        line_scores = None
        all_teams = []

        for result_set in self.data["resultSets"]:
            if result_set["name"] == "GameHeader":
                game_header = result_set
            elif result_set["name"] == "LineScore":
                line_scores = result_set
            elif result_set["name"] == "WestConfStandingsByDay":
                all_teams.append(result_set)
            elif result_set["name"] == "EastConfStandingsByDay":
                all_teams.append(result_set)

        if not game_header or not line_scores:
            return extracted_games

        game_header_map = self._prepare_game_header_map(game_header)
        line_score_map = self._prepare_line_score_map(line_scores)
        team_map = self._prepare_team_map(all_teams)

        for key, value in game_header_map.items():
            line_score_data = line_score_map[key]

            home_team_id = value.get("HOME_TEAM_ID")
            team_data = team_map.get(home_team_id)
            home_line_score = list(filter(lambda element: element["TEAM_ID"] == home_team_id, line_score_data))[0]
            home_team = self._get_team_data(home_line_score, team_data)

            visitor_team_id = value.get("VISITOR_TEAM_ID")
            team_data = team_map.get(visitor_team_id)
            visitor_line_score = list(filter(lambda element: element["TEAM_ID"] == visitor_team_id, line_score_data))[0]
            visitor_team = self._get_team_data(visitor_line_score, team_data)

            game_id = "_".join([self._format_date(value.get("GAME_DATE_EST")),
                                home_line_score["TEAM_ABBREVIATION"],
                                visitor_line_score["TEAM_ABBREVIATION"],
                                "NBA_API"
                                ])

            game = Game(
                home_team=home_team, visitor_team=visitor_team,
                home_team_score=home_line_score.get("PTS"),
                visitor_team_score=visitor_line_score.get("PTS"),
                date=self._format_date(value.get("GAME_DATE_EST")),
                season=value.get("SEASON"),
                game_id=game_id,
                source="NBA_API"
            )
            extracted_games.append(game)

        print(extracted_games)
        return extracted_games

    def _format_date(self, date_string):
        date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date

    def _prepare_game_header_map(self, data):
        game_header_map = {}
        headers = data["headers"]
        for row in data["rowSet"]:
            game_data = dict(zip(headers, row))
            game_header_map[game_data.get("GAME_ID")] = game_data

        return game_header_map

    def _prepare_line_score_map(self, data):
        game_header_map = {}
        headers = data["headers"]
        for row in data["rowSet"]:
            game_data = dict(zip(headers, row))
            if game_data.get("GAME_ID") not in game_header_map:
                game_header_map[game_data.get("GAME_ID")] = [game_data]
            else:
                game_header_map[game_data.get("GAME_ID")].append(game_data)

        return game_header_map

    def _prepare_team_map(self, data):
        game_header_map = {}

        for inner_data in data:
            headers = inner_data["headers"]
            for row in inner_data["rowSet"]:
                game_data = dict(zip(headers, row))
                game_header_map[game_data.get("TEAM_ID")] = game_data

        return game_header_map

    def _get_team_data(self, selected_line_score, team_data):
        team = Team(conference=team_data.get("CONFERENCE"),
                    division=nba_divisions.get(selected_line_score["TEAM_ABBREVIATION"]),
                    city=selected_line_score["TEAM_CITY_NAME"],
                    name=selected_line_score["TEAM_NAME"],
                    full_name=" ".join([selected_line_score["TEAM_CITY_NAME"],
                                        selected_line_score["TEAM_NAME"]]),
                    abbreviation=selected_line_score["TEAM_ABBREVIATION"]
                    )
        return team