"""Real-world cases for tictactoe.py: the board arrives from someone else.

A share link like /play?board=XXXOOO... is untrusted input. A well-formed string can still
describe a game nobody could have played. The book checks the shape; these check sense.
"""

from subprocess import getstatusoutput

prg = "./tictactoe.py"


def fails(args: str, why: str) -> None:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv != 0, out
    assert why in out


def test_two_winners_is_impossible():
    """X and O can't both have three in a row"""
    fails("-b XXXOOO...", "impossible")


def test_turns_alternate():
    """five X and no O can't happen"""
    fails("-b XXXXX....", "impossible")
    fails("-b OOOO.X...", "impossible")


def test_no_moves_after_a_win():
    """once X has won, O can't play on"""
    fails("-b XXXOO.... -p O -c 6", "already won")


def test_lowercase_is_rejected_not_guessed():
    """'x' isn't 'X': reject it rather than guess"""
    fails("-b x........", "must be 9 characters")


def test_a_real_game_still_plays():
    """a legal mid-game board takes the next move"""
    rv, out = getstatusoutput(f"{prg} -b XO.XO.... -p X -c 7")
    assert rv == 0
    assert out.splitlines()[-1] == "X has won!"
