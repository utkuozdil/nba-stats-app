import json

from src.model.player.player import Player
from src.model.team.team import Team


class NBAAPITeamDataExtractor:

    def __init__(self, data, season, game_id):
        self.data = json.loads(data) if isinstance(data, str) else data
        self.season = season
        self.game_id = game_id

    def extract_team_data(self, is_win, team_data, is_visitor):
        if len(self.data) > 0:
            team = Team.model_validate(self.data[0])
            if self.game_id not in team.game_ids:
                team.game_count += 1
                if is_win:
                    team.win_count += 1
                else:
                    team.loss_count += 1
                if is_visitor:
                    team.visitor_win_count += 1 if is_win else 0
                    team.visitor_loss_count += 0 if is_win else 1
                else:
                    team.home_win_count += 1 if is_win else 0
                    team.home_loss_count += 0 if is_win else 1
                team.game_ids.add(self.game_id)
        else:
            team = Team(team_id=team_data.abbreviation, season=self.season, team_name=team_data.full_name,
                        conference=team_data.conference, division=team_data.division,
                        abbreviation=team_data.abbreviation, city=team_data.city, name=team_data.name, game_count=1,
                        win_count=1 if is_win else 0, loss_count=0 if is_win else 1, game_ids={self.game_id},
                        home_win_count=1 if is_visitor else 0, home_loss_count=0 if is_visitor else 1,
                        visitor_win_count=1 if not is_visitor else 0,
                        visitor_loss_count=0 if not is_visitor else 1)
        return team