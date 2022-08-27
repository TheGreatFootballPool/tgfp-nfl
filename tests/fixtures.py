""" Test fixtures for all the tests """
import json
import pytest
from tgfp_nfl import TgfpNfl


@pytest.fixture
def tgfp_nfl_obj() -> TgfpNfl:
    """
    This will return the default tgfp database object loaded with the test fixture

    :return: tgfp database object
    :rtype: TGFP
    """
    with open('data/team_data.json', 'r', encoding='utf-8') as team_json_data:
        teams_data: dict = json.load(team_json_data)
    with open('data/games_data.json', 'r', encoding='utf-8') as game_json_data:
        games_data: dict = json.load(game_json_data)
    patched_tgfp = TgfpNfl(week_no=1)
    patched_tgfp._games_data = games_data
    patched_tgfp._teams_data = teams_data
    return patched_tgfp
