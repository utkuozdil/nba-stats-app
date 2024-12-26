import json

from src.model.player.player import Player


class NBAAPIPlayerDataExtractor:

    def __init__(self, data, season, game_id):
        self.data = json.loads(data)
        self.season = season
        self.game_id = game_id

    def extract_players_data(self):
        all_players = []
        all_players.extend(self._extract_players(self.data.get("boxScoreTraditional", {}).get("homeTeam", {})))
        all_players.extend(self._extract_players(self.data.get("boxScoreTraditional", {}).get("awayTeam", {})))
        return all_players

    def _extract_players(self, team_data):
        player_list = []
        team_name = " ".join([team_data.get("teamCity"), team_data.get("teamName")])
        players = team_data.get("players", [])
        for player_data in players:
            player_name = " ".join([player_data.get("firstName"), player_data.get("familyName")])
            stats = player_data.get("statistics", {})

            player = Player(player_name=player_name, team_name=team_name, season=self.season,
                            position=player_data.get("position"), minutes_played=stats.get("minutes"),
                            three_pointers_made=stats.get("threePointersMade"), player_id=player_name,
                            three_pointers_attempted=stats.get("threePointersAttempted"),
                            turnover_count=stats.get("turnovers"), game_count= 1,
                            field_goals_made=stats.get("fieldGoalsMade"), total_rebound=stats.get("reboundsTotal"),
                            field_goals_attempted=stats.get("fieldGoalsAttempted"), steal_count=stats.get("steals"),
                            free_throws_made=stats.get("freeThrowsMade"), plus_minus_stat=stats.get("plusMinusPoints"),
                            free_throws_attempted=stats.get("freeThrowsAttempted"), point_count=stats.get("points"),
                            offensive_rebound=stats.get("reboundsOffensive"), assist_count=stats.get("assists"),
                            defensive_rebound=stats.get("reboundsDefensive"), block_count=stats.get("blocks")
                            )
            player.game_ids.add(self.game_id)
            player_list.append(player)
        return player_list
