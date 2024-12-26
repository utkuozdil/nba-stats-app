from decimal import Decimal
from typing import Set
from pydantic import BaseModel


class PlayerAdvanced(BaseModel):
    player_id: str  # Partition Key
    season: int  # Sort Key
    player_name: str
    team_name: str
    ts_percentage: Decimal  # True Shooting Percentage
    efg_percentage: Decimal  # Effective Field Goal Percentage
    usage_rate: Decimal  # Usage Rate
    rebound_percentage: Decimal  # Total Rebound Percentage
    assist_percentage: Decimal  # Assist Percentage
    turnover_percentage: Decimal  # Turnover Percentage
    pie: Decimal  # Player Impact Estimate
    off_rating: Decimal  # Offensive Rating
    def_rating: Decimal  # Defensive Rating
    net_rating: Decimal  # Net Rating
    ast_to: Decimal  # Assist-to-Turnover Ratio
    ast_ratio: Decimal  # Assist Ratio
    oreb_percentage: Decimal  # Offensive Rebound Percentage
    dreb_percentage: Decimal  # Defensive Rebound Percentage
    pace: Decimal  # Game Pace
    game_ids: Set[str] = set()  # List of processed game IDs
    total_attempts: int = 0
    field_goals_attempted: int = 0
    minutes_played_as_float: Decimal = 0
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }
