import time
from src.utility.populator.game_and_team_populator import GameAndTeamPopulator
from src.utility.populator.player_populator import PlayerPopulator


start_date = "2024-10-22"
end_date = "2024-12-27"

game_and_team_populator = GameAndTeamPopulator(start_date=start_date, end_date=end_date)
game_and_team_populator.populate_data()
time.sleep(10)
player_populator = PlayerPopulator(start_date=start_date, end_date=end_date)
player_populator.populate_player_data(start_date, end_date)
