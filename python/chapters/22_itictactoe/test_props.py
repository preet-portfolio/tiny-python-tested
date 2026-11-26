"""Properties of the game state, over move sequences Hypothesis makes up.

Whatever anyone types, in any order, the game has to stay a game that could really happen.
"""

import importlib.util
import os

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("ittt", os.path.abspath("itictactoe.py"))
game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)

SETTINGS = settings(max_examples=150, derandomize=True, deadline=None, database=None)
typed = st.lists(st.sampled_from(list("123456789") * 3 + ["q", "0", "10", "x", " 5", ""]),
                 max_size=20)


def states(moves):
    state = game.State()
    yield state
    for move in moves:
        state = game.get_move(state, move)
        yield state


@SETTINGS
@given(typed)
def test_turns_stay_fair(moves):
    """at every moment X has the same number of moves as O, or one more"""
    for state in states(moves):
        assert state.board.count("X") - state.board.count("O") in (0, 1)


@SETTINGS
@given(typed)
def test_each_move_fills_at_most_one_square(moves):
    """a move changes one square or none, and never rubs one out"""
    previous = game.State()
    for state in list(states(moves))[1:]:
        changed = [i for i in range(9) if previous.board[i] != state.board[i]]
        assert len(changed) <= 1
        assert all(previous.board[i] == "." for i in changed)
        previous = state


@SETTINGS
@given(typed)
def test_never_two_winners(moves):
    """X and O never both have three in a row"""
    for state in states(moves):
        b = state.board
        wins = {b[i] for i, j, k in game.WINS if b[i] == b[j] == b[k] != "."}
        assert len(wins) <= 1


@SETTINGS
@given(typed)
def test_draw_means_full_and_no_winner(moves):
    """a draw only happens on a full board with no winner"""
    for state in states(moves):
        if state.draw:
            assert "." not in state.board and state.winner is None
            assert game.find_winner(state.board) is None


@SETTINGS
@given(typed)
def test_game_over_means_nothing_changes(moves):
    """once the game is over, more typing changes nothing"""
    final = list(states(moves))[-1]
    if final.winner or final.draw or final.quit:
        after = game.get_move(final, "5")
        assert after.board == final.board and after.winner == final.winner
