from pydantic import BaseModel

from src.model.game.teamdata import TeamData


class Game(BaseModel):
    game_id: str
    date: str
    season: int
    home_team_score: int
    visitor_team_score: int
    home_team: TeamData
    visitor_team: TeamData
    source: str