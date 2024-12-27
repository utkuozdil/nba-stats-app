from src.model.game.game import Game
from src.model.game.teamdata import TeamData
from src.model.team.team import Team
from src.services.aws.dynamodb import DynamoDB
from src.utility.extractor.nba_api_team_data_extractor import NBAAPITeamDataExtractor
from src.utility.util.config import TEAM_TABLE_NAME, TEAM_TABLE_NAME_INDEX

dynamodb = DynamoDB(TEAM_TABLE_NAME)


def handler(event, context):
    print(event)
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                new_image = record['dynamodb']['NewImage']
                game_data = {k: parse_dynamodb_item(v) for k, v in new_image.items()}

                if game_data.get('source') == 'NBA_API':
                    game = Game.model_validate(game_data)

                    home_team = update_team_data(game.home_team, game.season,
                                                 game.home_team_score > game.visitor_team_score,
                                                 game_data.get("game_id"), False)
                    visitor_team = update_team_data(game.visitor_team, game.season,
                                                    game.visitor_team_score > game.home_team_score,
                                                    game_data.get("game_id"), True)

                    dynamodb.save_batch([home_team, visitor_team])
    except Exception as e:
        print(f"Error processing DynamoDB stream: {str(e)}")
        raise


def parse_dynamodb_item(dynamodb_item):
    if 'S' in dynamodb_item:
        return dynamodb_item['S']
    elif 'N' in dynamodb_item:
        return int(dynamodb_item['N'])
    elif 'M' in dynamodb_item:
        return {k: parse_dynamodb_item(v) for k, v in dynamodb_item['M'].items()}
    elif 'L' in dynamodb_item:
        return [parse_dynamodb_item(v) for v in dynamodb_item['L']]
    else:
        return None


def update_team_data(team_data: TeamData, season: int, is_win: bool, game_id: str, is_visitor: bool):
    teams = dynamodb.get_by_index_value(index_name=TEAM_TABLE_NAME_INDEX, key="team_name",
                                        value=team_data.full_name, sort_key="season",
                                        sort_value=season)
    
    nba_api_team_data_extractor = NBAAPITeamDataExtractor(teams, season, game_id)
    team = nba_api_team_data_extractor.extract_team_data(is_win, team_data, is_visitor)
    
    return team
