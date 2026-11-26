"""Real-world cases for telephone.py: fuzzing a parser with mutated input.

Feeding a program slightly broken input (fuzzing) finds crashes nobody thought to test. A
fuzzer is only useful if it really changes something, reports the same mutation for the same
seed, and leaves the shape of the input alone so the parser gets past line one. Every case
here must pass without breaking a single test in the author's test.py.
"""

from subprocess import getstatusoutput

prg = "./telephone.py"


def heard(args: str) -> tuple[str, str]:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv == 0, out
    said, got = out.split('\nI heard : "')
    return said.removeprefix('You said: "')[:-1], got[:-1]


def diff(a: str, b: str) -> int:
    assert len(a) == len(b)
    return sum(x != y for x, y in zip(a, b))


def test_short_message_still_changes():
    """10% of a 3-letter word is 0.3 letters: still make one mistake, or the fuzzer does nothing"""
    said, got = heard("-s 1 'Hi!'")
    assert diff(said, got) == 1


def test_half_rounds_the_same_way():
    """'abcde' at 10% is half a letter: one mistake"""
    said, got = heard("-s 4 -m .1 abcde")
    assert diff(said, got) == 1


def test_line_breaks_stay_put():
    """a three-line message is still three lines, with every line break in its place"""
    text = "name,age\nAda,36\nAlan,41"
    _, got = heard(f"-s 2 -m 1 '{text}'")
    assert len(got.split("\n")) == 3
    assert [i for i, c in enumerate(got) if c == "\n"] == [i for i, c in enumerate(text) if c == "\n"]


def test_exact_number_of_mistakes():
    """40% of a 20-letter message is exactly 8 changed letters"""
    said, got = heard("-s 7 -m .4 abcdefghijklmnopqrst")
    assert diff(said, got) == 8


def test_same_seed_same_mistakes():
    """one seed, run twice, gives one message"""
    assert heard("-s 11 'Pass it on'") == heard("-s 11 'Pass it on'")


def test_everything_changes_at_100_percent():
    """-m 1 changes every single letter"""
    said, got = heard("-s 3 -m 1 'aaaa bbbb'")
    assert diff(said, got) == len(said)
