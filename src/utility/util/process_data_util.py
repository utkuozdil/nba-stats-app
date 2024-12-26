from decimal import Decimal


def filter_games(extracted_games, previously_recorded_games):
    prev_recorded_unified_games = list(
        filter(lambda x: x["source"] == "NBA_API", previously_recorded_games))
    prev_recorded_unified_game_ids = set([x["game_id"]
                                          for x in prev_recorded_unified_games])
    filtered_games = []
    for extracted_game in extracted_games:
        if extracted_game.game_id not in prev_recorded_unified_game_ids:
            filtered_games.append(extracted_game)
    return filtered_games

def convert_decimals(obj):

    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

