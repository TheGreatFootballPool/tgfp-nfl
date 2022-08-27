""" Test NFL Teams """
from fixtures import tgfp_nfl_obj  # pylint: disable=unused-import
from tgfp_nfl import TgfpNfl, TgfpNflTeam
shutup_pylint = tgfp_nfl_obj


def test_team(tgfp_nfl_obj: TgfpNfl):
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
