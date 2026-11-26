"""Real-world cases for gematria.py: adding up codes is a (weak) checksum.

Summing character codes is the simplest checksum there is. These tests pin down what it
can and can't tell apart, and make sure non-English text and stray punctuation don't
quietly turn into wrong numbers.
"""

from subprocess import getoutput

prg = "./gematria.py"


def nums(text: str) -> list[str]:
    return getoutput(f'{prg} "{text}"').split()


def test_anagrams_collide():
    """'listen' and 'silent' use the same letters, so they get the same number"""
    a, b = nums("listen silent")
    assert a == b


def test_case_matters():
    """'Apple' and 'apple' are different numbers (A and a have different codes)"""
    a, b = nums("Apple apple")
    assert a != b


def test_accents_count_as_their_letter():
    """café counts like cafe, not like caf"""
    assert nums("café cafe") == nums("cafe cafe")
    assert nums("naïve") == nums("naive")


def test_lone_punctuation_is_not_a_word():
    """'wait -- what' gives two numbers, not a 0 in the middle"""
    assert nums("wait -- what") == nums("wait what")
    assert "0" not in nums("hello ! world 🙂")


def test_digits_count():
    """digits are counted by their codes too: '7' is 55"""
    assert nums("7") == ["55"]


def test_blank_lines_stay():
    """a blank line in the text is a blank line in the numbers"""
    assert getoutput(f"{prg} ../inputs/sonnet-29.txt").splitlines()[2] == ""
