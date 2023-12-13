""" Test fixtures for all the tests """
import json
from typing import List

import pytest
from tgfp_nfl import TgfpNfl


@pytest.fixture
def tgfp_nfl_obj() -> TgfpNfl:
    """
    This will return the default tgfp database object loaded with the test fixture

    :return: tgfp database object
    :rtype: TGFP
    """
    with open('data/nfl_team_data.json', 'r', encoding='utf-8') as team_json_data:
        teams_data: dict = json.load(team_json_data)
    with open('data/nfl_game_data.json', 'r', encoding='utf-8') as game_json_data:
        games_data: dict = json.load(game_json_data)
    with open('data/nfl_standings_data.json', 'r', encoding='utf-8') as standing_json_data:
        standings_data: dict = json.load(standing_json_data)
    patched_tgfp = TgfpNfl(week_no=1)
    patched_tgfp._games_source_data = games_data['events']
    patched_tgfp._teams_source_data = teams_data['sports'][0]['leagues'][0]['teams']
    afc_standings: List = standings_data['children'][0]['standings']['entries']
    nfc_standings: List = standings_data['children'][1]['standings']['entries']
    all_standings: List = afc_standings + nfc_standings
    patched_tgfp._standings_source_data = all_standings
    return patched_tgfp


@pytest.fixture
def tgfp_nfl_obj_live() -> TgfpNfl:
    """
    This will return the default tgfp database object with live data for week 1

    :return: tgfp database object
    :rtype: TGFP
    """
    live_tgfp = TgfpNfl(week_no=1)
    return live_tgfp


@pytest.fixture
def tgfp_nfl_obj_live_week_19() -> TgfpNfl:
    """ Returns a TGFP object for wildcard weekend """
    live_tgfp = TgfpNfl(week_no=19)
    return live_tgfp


@pytest.fixture
def tgfp_nfl_obj_live_week_14() -> TgfpNfl:
    """ Returns a TGFP object for week 14 weekend """
    live_tgfp = TgfpNfl(week_no=14)
    return live_tgfp
