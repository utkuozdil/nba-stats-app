from typing import Set

from pydantic import BaseModel


class Team(BaseModel):
    team_id: str
    season: int
    team_name: str
    conference: str
    division: str
    abbreviation: str
    city: str
    name: str
    game_count: int
    win_count: int
    loss_count: int
    game_ids: Set[str] = set()
    home_win_count: int
    home_loss_count: int
    visitor_win_count: int
    visitor_loss_count: int 
