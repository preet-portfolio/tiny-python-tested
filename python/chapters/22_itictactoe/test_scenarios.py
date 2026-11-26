"""Game-state tests for itictactoe.py, plus whole games played through the keyboard.

The book has no command-line tests for this chapter: the program asks questions instead of
taking arguments. So these tests call get_move() directly, one move at a time, and also
feed a whole game in through STDIN, the way a player at the keyboard would.
"""

import importlib.util
import os
from subprocess import getstatusoutput

import pytest

prg = "./itictactoe.py"


@pytest.fixture(scope="module")
def game():
    spec = importlib.util.spec_from_file_location("itictactoe", os.path.abspath("itictactoe.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def play(game, *moves):
    state = game.State()
    for move in moves:
        state = game.get_move(state, move)
    return state


def test_new_game_is_empty(game):
    """a new game: empty board, X to play, nobody has won"""
    state = game.State()
    assert state.board == "........." and state.player == "X"
    assert not state.winner and not state.draw and not state.quit


def test_players_take_turns(game):
    """X plays, then O, then X"""
    state = play(game, "1", "5")
    assert state.board == "X...O...." and state.player == "X"


def test_taken_cell_is_an_error(game):
    """playing on a taken cell is refused and it's still the same player's turn"""
    state = play(game, "1", "1")
    assert state.error == 'Cell "1" already taken'
    assert state.player == "O" and state.board == "X........"


def test_bad_cells_are_errors(game):
    """'biscuit', '0', '10' and nothing at all are not cells"""
    for bad in ("biscuit", "0", "10", ""):
        state = play(game, bad)
        assert state.error == f'Invalid cell "{bad}", please use 1-9'
        assert state.player == "X" and state.board == "........."


def test_spaces_around_a_move_are_fine(game):
    """' 5 ' means cell 5"""
    assert play(game, " 5 ").board == "....X...."


def test_q_quits(game):
    """typing q (or Q) ends the game"""
    assert play(game, "1", "Q").quit


def test_a_win(game):
    """three Xs across the top: X wins"""
    state = play(game, "1", "4", "2", "5", "3")
    assert state.winner == "X" and not state.draw


def test_ninth_move_win_is_a_win_not_a_draw(game):
    """when the very last square makes three in a row, that's a win, not a draw"""
    state = play(game, "1", "2", "3", "4", "5", "6", "8", "7", "9")
    assert state.board == "XOXOXOOXX"
    assert state.winner == "X" and not state.draw


def test_a_real_draw(game):
    """a full board with no three in a row is a draw"""
    state = play(game, "1", "2", "3", "5", "4", "6", "8", "7", "9")
    assert state.board == "XOXXOOOXX"
    assert state.draw and state.winner is None


def test_no_moves_after_the_game_is_won(game):
    """once X has won, O can't sneak in another move"""
    won = play(game, "1", "4", "2", "5", "3")
    after = game.get_move(won, "9")
    assert after.board == won.board and after.winner == "X"


def test_old_state_is_never_changed(game):
    """making a move gives a new game state; the old one stays exactly as it was"""
    before = play(game, "1")
    snapshot = (before.board, before.player, before.error, before.winner)
    game.get_move(before, "5")
    game.get_move(before, "1")
    assert (before.board, before.player, before.error, before.winner) == snapshot


def keyboard(name: str, moves: list[str]) -> tuple[int, str]:
    """Type the moves into the program (the file is left behind so it can be rerun)."""
    path = f"moves-{name}.txt"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(moves) + "\n")
    return getstatusoutput(f"{prg} < {path}")


def test_whole_game_at_the_keyboard():
    """a full game typed in: the last thing said is who won"""
    rv, out = keyboard("x-wins", ["1", "4", "2", "5", "3"])
    assert rv == 0
    assert out.splitlines()[-1] == "X has won!"
    assert "| X | X | X |" in out


def test_keyboard_runs_out_of_moves():
    """if the moves stop before the game ends, say goodbye instead of crashing"""
    rv, out = keyboard("short", ["1", "5"])
    assert rv == 0
    assert "Traceback" not in out
    assert out.rstrip().endswith("Bye!")
