from fixtures import tgfp_nfl_obj, tgfp_nfl_obj_live
from tgfp_nfl import TgfpNfl, TgfpNflTeam, TgfpNflGame, TgfpNflOdd

shutup_pylint = tgfp_nfl_obj
shutup_pylint2 = tgfp_nfl_obj_live


def test_teams(tgfp_nfl_obj: TgfpNfl):
    """
    Test all the teams and their information
    @type tgfp_nfl_obj: TgfpNfl
    """
    teams = tgfp_nfl_obj.teams()
    assert len(teams) == 32
    team_1: TgfpNflTeam = tgfp_nfl_obj.teams()[0]
    assert team_1.full_name == 'Arizona Cardinals'
    assert team_1.city == 'Arizona'
    assert team_1.long_name == 'Cardinals'
    assert team_1.short_name == 'ari'
    assert team_1.logo_url == \
           'https://a.espncdn.com/i/teamlogos/nfl/500/ari.png'
    assert team_1.id == 's:20~l:28~t:22'
    assert team_1.losses == 0
    assert team_1.wins == 0
    assert team_1.ties == 0


def test_games(tgfp_nfl_obj: TgfpNfl):
    """ Test the 'game' object  """
    assert len(tgfp_nfl_obj.games()) == 16
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    print(game_1)
    away_team = game_1.away_team
    assert isinstance(away_team, TgfpNflTeam)
    assert isinstance(game_1.home_team, TgfpNflTeam)
    assert game_1.id.startswith('s:20~l:28~')
    assert game_1.score_is_final is False
    assert game_1.game_status_type == 'STATUS_SCHEDULED'


def test_odds(tgfp_nfl_obj: TgfpNfl):
    for game in tgfp_nfl_obj.games():
        odd: TgfpNflOdd = game.odds
        assert len(odd.favored_team_short_name) >= 2
        assert len(odd.favored_team_short_name) <= 3
        assert isinstance(odd.favored_team_spread, float)
        assert odd.favored_team_spread > 0


def test_find_games(tgfp_nfl_obj: TgfpNfl):
    assert tgfp_nfl_obj.games() == tgfp_nfl_obj.find_games()


def test_find_teams(tgfp_nfl_obj: TgfpNfl):
    found_teams: [TgfpNflTeam] = tgfp_nfl_obj.find_teams('s:20~l:28~t:4')
    assert len(found_teams) == 1
    found_team: TgfpNflTeam = found_teams[0]
    assert found_team.full_name == 'Cincinnati Bengals'


def test_tgfp_nfl_odd(tgfp_nfl_obj: TgfpNfl):
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    odd_1: TgfpNflOdd = game_1.odds
    assert odd_1.favored_team_spread == 2.5


def test_api(tgfp_nfl_obj_live: TgfpNfl):
    assert len(tgfp_nfl_obj_live.games()) > 10
    assert len(tgfp_nfl_obj_live.games()) < 20
    assert len(tgfp_nfl_obj_live.teams()) == 32
    assert len(tgfp_nfl_obj_live.standings()) == 32


def test_get_schedule(tgfp_nfl_obj_live):
    games = tgfp_nfl_obj_live.games()
    assert len(games) == 16
    raw_games = tgfp_nfl_obj_live._games_source_data
    assert len(raw_games) == 16
