"""Real-world cases for apples.py: the song has to work on real words.

The book shows eight different ways to write this program; the tests are what make it safe
to swap one for another. These add words from real menus and real typing: accents, and a
capital letter in the option. Every case here must pass without breaking a single test in the
author's test.py.
"""

from subprocess import getstatusoutput

prg = "./apples.py"


def sing(args: str) -> str:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv == 0, out
    return out


def test_accented_vowels():
    """é, è, û and friends are vowels too"""
    assert sing("'Crème brûlée'") == "Crama bralaa"
    assert sing("-v i 'Éclair'") == "Icliir"


def test_accents_typed_as_two_pieces():
    """an e with its accent added separately (e + ́) still counts as one vowel"""
    assert sing("-v o 'café'") == "cofo"


def test_capital_vowel_option():
    """-v O works as well as -v o"""
    assert sing("-v O 'bar'") == "bor"
    assert sing("--vowel U 'APPLES'") == "UPPLUS"


def test_still_rejects_non_vowels():
    """-v x is still not a vowel"""
    rv, out = getstatusoutput(f"{prg} -v X foo")
    assert rv != 0
    assert out.lower().startswith("usage")


def test_only_vowels_change():
    """consonants, spaces, digits and y stay exactly where they were"""
    text = "Rhythm & blues, 1999!"
    out = sing(f"-v e '{text}'")
    assert len(out) == len(text)
    for a, b in zip(text, out):
        assert a == b or a.lower() in "aeiou"
    assert out == "Rhythm & blees, 1999!"


def test_singing_twice():
    """singing the song again with the same vowel changes nothing"""
    once = sing("-v u 'Apples and Bananas'")
    assert sing(f"-v u '{once}'") == once
