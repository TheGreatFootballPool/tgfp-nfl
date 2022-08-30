from fixtures import tgfp_nfl_obj  # pylint: disable=unused-import
from tgfp_nfl import TgfpNfl, TgfpNflTeam, TgfpNflGame, TgfpNflOdd

shutup_pylint = tgfp_nfl_obj


def test_teams(tgfp_nfl_obj: TgfpNfl):
    """
    Test all the teams and their information
    @type tgfp_nfl_obj: TgfpNfl
    """
    teams = tgfp_nfl_obj.teams()
    assert len(teams) == 32
    team_1: TgfpNflTeam = tgfp_nfl_obj.teams()[0]
    assert team_1.full_name == 'Cincinnati Bengals'
    assert team_1.logo_url == \
           'https://s.yimg.com/cv/apiv2/default/nfl/20190724/70x70/2019_CIN_wbg.png'
    assert team_1.id == 'nfl.t.4'
    assert team_1.losses == '2'
    assert team_1.wins == '0'
    assert team_1.ties == '0'


def test_games(tgfp_nfl_obj: TgfpNfl):
    """ Test the 'game' object  """
    assert len(tgfp_nfl_obj.games()) == 16
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    print(game_1)
    assert isinstance(game_1.away_team, TgfpNflTeam)
    assert isinstance(game_1.home_team, TgfpNflTeam)
    assert game_1.id.startswith('nfl.g.2')
    assert game_1.score_is_final is False
    assert game_1.status_type == 'pregame'


def test_odds(tgfp_nfl_obj: TgfpNfl):
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    assert len(game_1.odds()) == 1


def test_average_home_spread(tgfp_nfl_obj: TgfpNfl):
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    assert len(game_1.odds()) == 1
    odd_1: TgfpNflOdd = game_1.odds()[0]
    assert odd_1.home_spread == '2.5'
    assert game_1.average_home_spread() == 2.5


def test_find_games(tgfp_nfl_obj: TgfpNfl):
    assert tgfp_nfl_obj.games() == tgfp_nfl_obj.find_games()


def test_find_teams(tgfp_nfl_obj: TgfpNfl):
    found_teams: [TgfpNflTeam] = tgfp_nfl_obj.find_teams('nfl.t.4')
    assert len(found_teams) == 1
    found_team: TgfpNflTeam = found_teams[0]
    assert found_team.full_name == 'Cincinnati Bengals'


def test_tgfp_nfl_odd(tgfp_nfl_obj: TgfpNfl):
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    odd_1: TgfpNflOdd = game_1.odds()[0]
    assert odd_1.home_spread == '2.5'


def test_api():
    tgfp_nfl_obj: TgfpNfl = TgfpNfl(week_no=1)
    assert len(tgfp_nfl_obj.games()) > 10
    assert len(tgfp_nfl_obj.games()) < 20
