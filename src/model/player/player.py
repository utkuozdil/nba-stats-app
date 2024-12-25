from decimal import Decimal
from typing import Set

from pydantic import BaseModel

class Player(BaseModel):
    player_id: str
    player_name: str
    position: str
    season: int
    team_name: str
    point_count: int
    game_count: int
    offensive_rebound: int
    defensive_rebound: int
    total_rebound: int
    assist_count: int
    steal_count: int
    block_count: int
    turnover_count: int
    plus_minus_stat: Decimal
    field_goals_made: int
    field_goals_attempted: int
    free_throws_made: int
    free_throws_attempted: int
    three_pointers_made: int
    three_pointers_attempted: int
    minutes_played: str
    game_ids: Set[str] = set()