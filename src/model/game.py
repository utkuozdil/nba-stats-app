from pydantic import BaseModel

from src.model.team import Team


class Game(BaseModel):
    game_id: str
    date: str
    season: int
    home_team_score: int
    visitor_team_score: int
    home_team: Team
    visitor_team: Team
    source: str