import json
import os
import time
from datetime import datetime, timedelta

from src.integrations.nbacom import NbaCom
from src.model.player.player import Player
from src.services.dynamodb import DynamoDB
from src.services.s3 import S3
from src.util.config import BUCKET_NAME, PLAYER_TABLE_NAME, PLAYER_TABLE_INDEX
from src.util.nba_api_game_data_extractor import NBAAPIDataExtractor
from src.util.nba_api_player_data_extractor import NBAAPIPlayerDataExtractor

s3 = S3(BUCKET_NAME)
nbaAPI = NbaCom()
dynamodb = DynamoDB(PLAYER_TABLE_NAME)

start_date = "2024-10-22"
end_date = "2024-12-25"
file_path = os.path.join(os.path.dirname(__file__), 'player_population_dates.json')


def populate_nba_api_player_data(query_date_param, end_date_param):
    while query_date_param != end_date_param:

        with open(file_path, 'r') as f:
            date_data = json.load(f)
            if query_date_param not in date_data:
                key = f"{query_date_param}/nba-api.json"

                stored_data = s3.retrieve_data_from_bucket(key=key)
                nba_api_game_data_extractor = NBAAPIDataExtractor(data=stored_data)
                game_ids_data = nba_api_game_data_extractor.extract_game_ids()
                if game_ids_data:
                    season = game_ids_data.get("season")
                    game_ids = game_ids_data.get("game_ids", [])
                    for game_id in game_ids:
                        handle_game_data(game_id, season)
                        time.sleep(2.5)

                date_data.append(query_date_param)
                print(f"{query_date_param} is executed...")

            else:
                print(f"{query_date_param} is already executed, continue...")

        with open(file_path, "w") as f:
            json.dump(date_data, f, indent=2)

        query_date_param = datetime.strptime(query_date_param, '%Y-%m-%d') + timedelta(days=1)
        query_date_param = query_date_param.strftime('%Y-%m-%d')


def handle_game_data(game_id, season):
    box_score = nbaAPI.get_box_score_for_games(game_id=game_id)
    nba_api_player_data_extractor = NBAAPIPlayerDataExtractor(data=box_score, season=int(season), game_id=game_id)
    all_players = nba_api_player_data_extractor.extract_players_data()

    team_names = get_team_names(all_players)
    previously_recorded_players = []
    for team_name in team_names:
        previously_recorded_players.extend(
            dynamodb.get_by_index_value(index_name=PLAYER_TABLE_INDEX, key="team_name", value=team_name,
                                        sort_key="season",
                                        sort_value=int(season)))
    previously_recorded_players = [Player.model_validate(x) for x in previously_recorded_players]

    updated_players = []
    all_players = list(filter(lambda x: x.minutes_played is not None and len(x.minutes_played) > 0, all_players))
    for player in all_players:
        selected_data_list = list(filter(lambda x: x.player_id == player.player_id, previously_recorded_players))
        if len(selected_data_list) > 0:
            selected_player = selected_data_list[0]
            game_id = list(player.game_ids)[0]
            if game_id not in selected_player.game_ids:
                updated_players.append(update_player_stats(selected_player, player))
            else:
                print(f"{game_id} is already stored for {player.player_name}")
        else:
            updated_players.append(player)

    dynamodb.save_batch(updated_players)


def update_player_stats(previous: Player, new_data: Player):
    updated = Player.model_copy(previous, deep=True, update=None)
    updated.turnover_count += new_data.turnover_count
    updated.total_rebound += new_data.total_rebound
    updated.point_count += new_data.point_count
    updated.game_count += 1
    updated.offensive_rebound += new_data.offensive_rebound
    updated.defensive_rebound += new_data.defensive_rebound
    updated.assist_count += new_data.assist_count
    updated.steal_count += new_data.steal_count
    updated.block_count += new_data.block_count
    updated.field_goals_made += new_data.field_goals_made
    updated.field_goals_attempted += new_data.field_goals_attempted
    updated.free_throws_made += new_data.free_throws_made
    updated.free_throws_attempted += new_data.free_throws_attempted
    updated.three_pointers_made += new_data.three_pointers_made
    updated.three_pointers_attempted += new_data.three_pointers_attempted
    updated.plus_minus_stat += new_data.plus_minus_stat

    updated.minutes_played = add_minutes(updated.minutes_played, new_data.minutes_played)

    updated.game_ids.update(new_data.game_ids)

    return updated


def add_minutes(old_min, new_min):
    if old_min and new_min:
        old_min_array = old_min.split(":")
        new_min_array = new_min.split(":")

        minutes = int(old_min_array[0]) + int(new_min_array[0])
        seconds = int(old_min_array[1]) + int(new_min_array[1])
        if seconds > 60:
            minutes += 1
            seconds -= 60
        return str(minutes) + ":" + str(seconds)
    elif old_min:
        return old_min
    elif new_min:
        return new_min
    else:
        return None


def get_team_names(data):
    result = set()
    for player in data:
        if player.team_name not in result:
            result.add(player.team_name)
    return list(result)


populate_nba_api_player_data(query_date_param=start_date, end_date_param=end_date)
