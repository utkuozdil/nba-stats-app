from src.model.game.game import Game
from src.model.game.teamdata import TeamData
from src.model.team.team import Team
from src.services.dynamodb import DynamoDB
from src.util.config import TEAM_TABLE_NAME, TEAM_TABLE_NAME_INDEX

dynamodb = DynamoDB(TEAM_TABLE_NAME)


def handler(event, context):
    print(event)
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                new_image = record['dynamodb']['NewImage']
                game_data = {k: parse_dynamodb_item(v) for k, v in new_image.items()}

                if game_data.get('source') == 'Unified':
                    game = Game.model_validate(game_data)

                    home_team = update_team_data(game.home_team, game.season,
                                                 game.home_team_score > game.visitor_team_score)
                    visitor_team = update_team_data(game.visitor_team, game.season,
                                                    game.visitor_team_score > game.home_team_score)

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


def update_team_data(team_data: TeamData, season: int, is_win: bool):
    teams = dynamodb.get_by_index_value(index_name=TEAM_TABLE_NAME_INDEX, key="team_name",
                                        value=team_data.full_name, sort_key="season",
                                        sort_value=season)
    if len(teams) > 0:
        team = Team.model_validate(teams[0])
        team.game_count += 1
        if is_win:
            team.win_count += 1
        else:
            team.loss_count += 1
    else:
        team = Team(team_id=team_data.abbreviation, season=season, team_name=team_data.full_name,
                    conference=team_data.conference, division=team_data.division,
                    abbreviation=team_data.abbreviation, city=team_data.city, name=team_data.name, game_count=1,
                    win_count=1 if is_win else 0, loss_count=0 if is_win else 1)
    return team
