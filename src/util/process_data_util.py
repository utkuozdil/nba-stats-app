from decimal import Decimal


def filter_games(extracted_games, previously_recorded_games):
    prev_recorded_unified_games = list(
        filter(lambda x: x["source"] == "Unified", previously_recorded_games))
    prev_recorded_unified_game_ids = set([x["game_id"]
                                          for x in prev_recorded_unified_games])
    filtered_games = []
    for extracted_game in extracted_games:
        temp_game_id = "_".join([extracted_game.date,
                                 extracted_game.home_team.abbreviation,
                                 extracted_game.visitor_team.abbreviation,
                                 "Unified"])
        if temp_game_id not in prev_recorded_unified_game_ids:
            filtered_games.append(extracted_game)
    return filtered_games

def generate_game_id(extracted_game, source):
    game_id = "_".join([extracted_game.date,
                        extracted_game.home_team.abbreviation,
                        extracted_game.visitor_team.abbreviation,
                        source
                        ])
    return game_id

def convert_decimals(obj):

    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

