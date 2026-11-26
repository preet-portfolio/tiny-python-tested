"""Real-world cases for friar.py: a locale transform has to leave real text readable.

Text transforms (a dialect, a "pirate mode", a reading-age rewrite) run on whatever users
type, including SHOUTED words. (Contractions are pinned by the book: its Dickinson test
expects "you're" to become "y'all're", so these tests leave that alone.)
"""

from subprocess import getoutput

prg = "./friar.py"


def fry(text: str) -> str:
    return getoutput(f'{prg} "{text}"').strip()


def test_shouted_you():
    """YOU becomes Y'ALL, not Y'all"""
    assert fry("YOU THERE") == "Y'ALL THERE"


def test_shouted_ing():
    """COOKING becomes COOKIN'"""
    assert fry("STOP COOKING") == "STOP COOKIN'"


def test_one_syllable_stays():
    """thing, king, string and bring keep their g"""
    assert fry("thing king string bring") == "thing king string bring"


def test_punctuation_and_spacing_kept():
    """commas, dashes and double spaces come out exactly as they went in"""
    assert fry("Are you  going -- or staying?") == "Are y'all  goin' -- or stayin'?"


def test_already_fried_is_unchanged():
    """running it on cookin' and y'all changes nothing"""
    assert fry("cookin' for y'all") == "cookin' for y'all"
