""" Test NFL Games """
import pytest

from tgfp_nfl import TgfpNfl, TgfpNflGame, TgfpNflTeam


# pylint: disable=redefined-outer-name
@pytest.fixture
def tgfp_nfl() -> TgfpNfl:
    """
    This will return the default tgfp database object loaded with the test fixture

    :return: tgfp database object
    :rtype: TGFP
    """
    return TgfpNfl(week_no=1)


def test_game(tgfp_nfl: TgfpNfl):
    """ Test the 'game' object  """
    # assert len(tgfp_nfl.games()) == 16
    game_1: TgfpNflGame = tgfp_nfl.games()[0]
    print(game_1)
    assert isinstance(game_1.away_team, TgfpNflTeam)
    assert isinstance(game_1.home_team, TgfpNflTeam)
    assert game_1.id.startswith('nfl.g.2')
    assert game_1.score_is_final == False
    assert game_1.status_type == 'pregame'
