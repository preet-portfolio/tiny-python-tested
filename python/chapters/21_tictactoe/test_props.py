"""Properties of find_winner(), on boards Hypothesis generates.

A winner doesn't depend on which way up you hold the board.
"""

import importlib.util
import os

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("ttt", os.path.abspath("tictactoe.py"))
ttt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ttt)

ROTATE = (6, 3, 0, 7, 4, 1, 8, 5, 2)
MIRROR = (2, 1, 0, 5, 4, 3, 8, 7, 6)
boards = st.text(alphabet=".XO", min_size=9, max_size=9)
SETTINGS = settings(max_examples=100, derandomize=True, deadline=None, database=None)


def apply(perm, board):
    return "".join(board[i] for i in perm)


@SETTINGS
@given(boards)
def test_rotating_keeps_the_winner(board):
    """turn the board a quarter turn: same winner"""
    assert ttt.find_winner(apply(ROTATE, board)) == ttt.find_winner(board)


@SETTINGS
@given(boards)
def test_mirroring_keeps_the_winner(board):
    """flip the board left to right: same winner"""
    assert ttt.find_winner(apply(MIRROR, board)) == ttt.find_winner(board)


@SETTINGS
@given(boards)
def test_swapping_players_swaps_the_winner(board):
    """swap every X and O: the other player wins"""
    swapped = board.translate(str.maketrans("XO", "OX"))
    other = {"X": "O", "O": "X", None: None}
    assert ttt.find_winner(swapped) == other[ttt.find_winner(board)]
