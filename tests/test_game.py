""" Test NFL Games """
from fixtures import tgfp_nfl_obj
from tgfp_nfl import TgfpNfl, TgfpNflGame, TgfpNflTeam
shutup_pylint = tgfp_nfl_obj


# pylint: disable=redefined-outer-name
def test_game(tgfp_nfl_obj: TgfpNfl):
    """ Test the 'game' object  """
    assert len(tgfp_nfl_obj.games()) == 16
    game_1: TgfpNflGame = tgfp_nfl_obj.games()[0]
    print(game_1)
    assert isinstance(game_1.away_team, TgfpNflTeam)
    assert isinstance(game_1.home_team, TgfpNflTeam)
    assert game_1.id.startswith('nfl.g.2')
    assert game_1.score_is_final is False
    assert game_1.status_type == 'pregame'
