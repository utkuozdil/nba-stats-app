import json

from src.model.player.player import Player
from src.model.player.player_advanced import PlayerAdvanced


class NBAAPIPlayerAdvancedDataExtractor:

    def __init__(self, data, season, game_id):
        self.data = json.loads(data)
        self.season = season
        self.game_id = game_id

    def extract_players_data(self):
        all_players = []
        all_players.extend(self._extract_players(self.data.get("boxScoreAdvanced", {}).get("homeTeam", {})))
        all_players.extend(self._extract_players(self.data.get("boxScoreAdvanced", {}).get("awayTeam", {})))
        return all_players

    def _extract_players(self, team_data):
        player_list = []
        team_name = " ".join([team_data.get("teamCity", ""), team_data.get("teamName", "")])
        players = team_data.get("players", [])
        for player_data in players:
            player_name = " ".join([player_data.get("firstName"), player_data.get("familyName")])
            stats = player_data.get("statistics", {})
            
            player = PlayerAdvanced(player_name=player_name, team_name=team_name, season=self.season, player_id=player_name, game_ids=set([self.game_id]),
                                    ts_percentage=stats.get("trueShootingPercentage"),
                                    efg_percentage=stats.get("effectiveFieldGoalPercentage"),                                  
                                    usage_rate=stats.get("usagePercentage"),
                                    rebound_percentage=stats.get("reboundPercentage"),
                                    assist_percentage=stats.get("assistPercentage"),
                                    turnover_percentage=stats.get("turnoverRatio"),
                                    pie=stats.get("PIE"),
                                    off_rating=stats.get("offensiveRating"),
                                    def_rating=stats.get("defensiveRating"),
                                    net_rating=stats.get("netRating"),
                                    ast_to=stats.get("assistToTurnover"),
                                    ast_ratio=stats.get("assistRatio"),
                                    oreb_percentage=stats.get("offensiveReboundPercentage"),
                                    dreb_percentage=stats.get("defensiveReboundPercentage"),
                                    pace=stats.get("pace"))
            player_list.append(player)
        return player_list
