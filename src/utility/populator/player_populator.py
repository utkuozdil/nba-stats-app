from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
import time
from src.integrations.nbacom import NbaCom
from src.model.player.player import Player
from src.model.player.player_advanced import PlayerAdvanced
from src.services.aws.dynamodb import DynamoDB
from src.services.aws.s3 import S3
from src.services.aws.sns import SNS
from src.utility.extractor.nba_api_advanced_player_data_extractor import NBAAPIPlayerAdvancedDataExtractor
from src.utility.extractor.nba_api_game_data_extractor import NBAAPIDataExtractor
from src.utility.extractor.nba_api_player_data_extractor import NBAAPIPlayerDataExtractor
from src.utility.util.config import BUCKET_NAME, PLAYER_ADVANCED_TABLE_INDEX, PLAYER_ADVANCED_TABLE_NAME, PLAYER_TABLE_INDEX, PLAYER_TABLE_NAME


class PlayerPopulator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.s3 = S3(BUCKET_NAME)
        self.dynamodb = DynamoDB(PLAYER_TABLE_NAME)
        self.dynamodb_advanced = DynamoDB(PLAYER_ADVANCED_TABLE_NAME)
        self.nbaAPI = NbaCom()
        self.file_path = os.path.join(os.path.dirname(__file__), 'player_population_dates.json')

    def populate_player_data(self, query_date_param, end_date_param):
        while query_date_param != end_date_param:

            with open(self.file_path, 'r') as f:
                date_data = json.load(f)
                if query_date_param not in date_data:
                    key = f"{query_date_param}/nba-api.json"

                    stored_data = self.s3.retrieve_data_from_bucket(key=key)
                    nba_api_game_data_extractor = NBAAPIDataExtractor(
                        data=stored_data)
                    game_ids_data = nba_api_game_data_extractor.extract_game_ids()
                    if game_ids_data:
                        season = game_ids_data.get("season")
                        game_ids = game_ids_data.get("game_ids", [])
                        for game_id in game_ids:
                            self.handle_game_data(game_id, season)
                            time.sleep(0.25)

                    date_data.append(query_date_param)
                    print(f"{query_date_param} is executed...")

                else:
                    print(f"{query_date_param} is already executed, continue...")

            with open(self.file_path, "w") as f:
                json.dump(date_data, f, indent=2)

            query_date_param = datetime.strptime(
                query_date_param, '%Y-%m-%d') + timedelta(days=1)
            query_date_param = query_date_param.strftime('%Y-%m-%d')

    def handle_game_data(self, game_id, season):
        box_score = self.nbaAPI.get_box_score_for_games(game_id=game_id)
        nba_api_player_data_extractor = NBAAPIPlayerDataExtractor(data=box_score, season=int(season), game_id=game_id)
        
        advanced_box_score = self.nbaAPI.get_advanced_box_score_for_games(game_id=game_id)
        nba_api_player_advanced_data_extractor = NBAAPIPlayerAdvancedDataExtractor(data=advanced_box_score, season=int(season), game_id=game_id)
        all_players = nba_api_player_data_extractor.extract_players_data()
        all_players_advanced = nba_api_player_advanced_data_extractor.extract_players_data()
        
        self.handle_basic_player_data(season, all_players)
        time.sleep(0.5)
        self.handle_advanced_player_data(season, all_players_advanced)

    def handle_basic_player_data(self, season, all_players):
        team_names = self.get_team_names(all_players)
        previously_recorded_players = []
        for team_name in team_names:
            previously_recorded_players.extend(
                self.dynamodb.get_by_index_value(index_name=PLAYER_TABLE_INDEX, key="team_name", value=team_name,
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
                    updated_players.append(self.update_player_stats(selected_player, player))
                else:
                    print(f"{game_id} is already stored for {player.player_name}")
            else:
                updated_players.append(player)

        self.dynamodb.save_batch(updated_players)
    
    def handle_advanced_player_data(self, season, all_players):
        team_names = self.get_team_names(all_players)
        previously_recorded_players = []
        for team_name in team_names:
            previously_recorded_players.extend(
                self.dynamodb_advanced.get_by_index_value(index_name=PLAYER_ADVANCED_TABLE_INDEX, key="team_name", value=team_name,
                                            sort_key="season",
                                            sort_value=int(season)))
            
        previously_recorded_players = [PlayerAdvanced.model_validate(x) for x in previously_recorded_players]
        
        updated_players = []
        for player in all_players:
            selected_data_list = list(filter(lambda x: x.player_id == player.player_id, previously_recorded_players))
            if len(selected_data_list) > 0:
                selected_player = selected_data_list[0]
                game_id = list(player.game_ids)[0]
                if game_id not in selected_player.game_ids:
                    basic_player_data = self.dynamodb.get_item(key={"player_id": player.player_id, "season": int(season)})
                    if basic_player_data:
                        basic_player = Player.model_validate(basic_player_data)
                        player.minutes_played_as_float = self.minutes_to_float(basic_player.minutes_played)
                        player.field_goals_attempted = basic_player.field_goals_attempted
                        player.total_attempts = (
                            basic_player.field_goals_attempted +
                            basic_player.free_throws_attempted
                        )
                        updated_players.append(self.update_player_advanced_stats(selected_player, player, basic_player_data))
                else:
                    print(f"{game_id} is already stored for {player.player_name}")
            else:
                basic_player_data = self.dynamodb.get_item(key={"player_id": player.player_id, "season": int(season)})
                if basic_player_data:
                    basic_player = Player.model_validate(basic_player_data)
                    player.minutes_played_as_float = self.minutes_to_float(basic_player.minutes_played)
                    player.field_goals_attempted = basic_player.field_goals_attempted
                    player.total_attempts = (
                        basic_player.field_goals_attempted +
                        basic_player.free_throws_attempted
                    )
                if player.minutes_played_as_float > 0:
                    updated_players.append(player)

        self.dynamodb_advanced.save_batch(updated_players)
    
    def update_player_advanced_stats(self, previous: PlayerAdvanced, new_data: PlayerAdvanced, basic_stats: Player):
        basic_stats = Player.model_validate(basic_stats)
        updated = PlayerAdvanced.model_copy(previous, deep=True, update=None)

        # Weighted averages using attempt counts from Player (basic stats)
        def weighted_average(old_value, old_weight, new_value, new_weight):
            total_weight = old_weight + new_weight
            if total_weight == 0:
                return Decimal('0.00')
            # Convert all values to Decimal and ensure 2 decimal places
            old_val = Decimal(str(old_value))
            new_val = Decimal(str(new_value))
            old_w = Decimal(str(old_weight))
            new_w = Decimal(str(new_weight))
            result = ((old_val * old_w) + (new_val * new_w)) / (old_w + new_w)
            return Decimal(str(round(float(result), 2)))

        # TS%: True Shooting Percentage
        total_attempts = basic_stats.field_goals_attempted + basic_stats.free_throws_attempted
        updated.ts_percentage = weighted_average(
            previous.ts_percentage,
            previous.total_attempts,  # Previous cumulative attempts
            new_data.ts_percentage,
            total_attempts - previous.total_attempts  # New attempts from this game
        )
        updated.total_attempts = total_attempts  # Update total attempts

        # EFG%: Effective Field Goal Percentage
        updated.efg_percentage = weighted_average(
            previous.efg_percentage,
            previous.field_goals_attempted,
            new_data.efg_percentage,
            basic_stats.field_goals_attempted - previous.field_goals_attempted
        )

        # Usage Rate
        updated.usage_rate = weighted_average(
            previous.usage_rate,
            previous.minutes_played_as_float,
            new_data.usage_rate,
            new_data.minutes_played_as_float
        )

        # Other percentage-based stats
        updated.rebound_percentage = weighted_average(
            previous.rebound_percentage,
            len(previous.game_ids),
            new_data.rebound_percentage,
            len(previous.game_ids)
        )
        updated.assist_percentage = weighted_average(
            previous.assist_percentage,
            len(previous.game_ids),
            new_data.assist_percentage,
            len(previous.game_ids)
        )
        updated.turnover_percentage = weighted_average(
            previous.turnover_percentage,
            len(previous.game_ids),
            new_data.turnover_percentage,
            len(previous.game_ids)
        )

        # Additive metrics
        updated.pie += new_data.pie
        updated.off_rating += new_data.off_rating
        updated.def_rating += new_data.def_rating
        updated.net_rating += new_data.net_rating
        updated.ast_to += new_data.ast_to
        updated.ast_ratio += new_data.ast_ratio
        updated.oreb_percentage = weighted_average(
            previous.oreb_percentage,
            len(previous.game_ids),
            new_data.oreb_percentage,
            len(previous.game_ids)
        )
        updated.dreb_percentage = weighted_average(
            previous.dreb_percentage,
            len(previous.game_ids),
            new_data.dreb_percentage,
            len(previous.game_ids)
        )
        updated.pace = weighted_average(
            previous.pace,
            previous.minutes_played_as_float,
            new_data.pace,
            new_data.minutes_played_as_float
        )
        
        # Update game IDs
        updated.game_ids.update(new_data.game_ids)
        
        return updated

    def update_player_stats(self,previous: Player, new_data: Player):
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

        updated.minutes_played = self.add_minutes(updated.minutes_played, new_data.minutes_played)

        updated.game_ids.update(new_data.game_ids)

        return updated

    def add_minutes(self, old_min, new_min):
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

    def get_team_names(self, data):
        result = set()
        for player in data:
            if player.team_name not in result:
                result.add(player.team_name)
        return list(result)

    def minutes_to_float(self, minutes_str: str) -> Decimal:
        if minutes_str is None or len(minutes_str) == 0:
            return Decimal('0.00')
        array = minutes_str.split(':')
        # Convert to string before creating Decimal and format to 2 decimal places
        return Decimal(f"{float(int(array[0])) + float(int(array[1]))/60:.2f}")
