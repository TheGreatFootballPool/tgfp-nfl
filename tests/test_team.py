""" Test NFL Teams """
import pytest

from tgfp_nfl import TgfpNfl, TgfpNflTeam


# pylint: disable=redefined-outer-name
@pytest.fixture
def tgfp_nfl() -> TgfpNfl:
    """
    This will return the default tgfp database object loaded with the test fixture

    :return: tgfp database object
    :rtype: TGFP
    """
    return TgfpNfl(week_no=1)


def test_team(tgfp_nfl: TgfpNfl):
    """
    Test all the teams and their information
    @type tgfp_nfl: TgfpNfl
    """
    teams = tgfp_nfl.teams()
    assert len(teams) == 32
    team_1: TgfpNflTeam = tgfp_nfl.teams()[0]
    assert team_1.full_name == 'Cincinnati Bengals'
    assert team_1.logo_url == \
           'https://s.yimg.com/cv/apiv2/default/nfl/20190724/70x70/2019_CIN_wbg.png'
    assert team_1.id == 'nfl.t.4'
    assert team_1.losses == '1'
    assert team_1.wins == '0'
    assert team_1.ties == '0'
