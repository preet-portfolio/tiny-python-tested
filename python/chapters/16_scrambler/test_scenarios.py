"""Real-world cases for scrambler.py: scrambled copy that people still have to read.

Designers scramble text to test how readable a layout is (and to show the famous "your
brain still reads it" trick). That only works if every word gets scrambled, in any
language, and nothing that is unreadable once scrambled (like an acronym) gets touched.
"""

from subprocess import getstatusoutput

prg = "./scrambler.py"


def scramble(text: str, seed: int) -> str:
    rv, out = getstatusoutput(f'{prg} -s {seed} "{text}"')
    assert rv == 0
    return out


def test_accented_words_get_scrambled_too():
    """'crème brûlée' is two words, and they get shuffled like any others"""
    outs = {scramble("crème brûlée délicieuse", s) for s in range(1, 8)}
    for i, word in enumerate(["crème", "brûlée", "délicieuse"]):
        assert any(out.split()[i] != word for out in outs)
    for out in outs:
        a, b, c = out.split()
        assert sorted(a) == sorted("crème") and a[0] == "c" and a[-1] == "e"
        assert sorted(b) == sorted("brûlée") and b[0] == "b" and b[-1] == "e"
        assert sorted(c) == sorted("délicieuse") and c[0] == "d" and c[-1] == "e"


def test_other_alphabets_are_words_too():
    """Russian and Greek words get scrambled, keeping their first and last letters"""
    outs = [scramble("привет καλημέρα", s) for s in range(1, 6)]
    assert any(out.split()[0] != "привет" for out in outs)
    assert any(out.split()[1] != "καλημέρα" for out in outs)
    for out in outs:
        a, b = out.split()
        assert a[0] == "п" and a[-1] == "т" and sorted(a) == sorted("привет")
        assert b[0] == "κ" and b[-1] == "α" and sorted(b) == sorted("καλημέρα")


def test_acronyms_stay_put():
    """NASA and HTML in capitals are left alone"""
    for s in range(1, 10):
        out = scramble("NASA uses HTML", s)
        assert out.split()[0] == "NASA" and out.split()[2] == "HTML"


def test_same_seed_same_scramble():
    """the same lucky number scrambles the same way"""
    text = "Readability matters for everyone"
    assert scramble(text, 5) == scramble(text, 5)


def test_numbers_and_punctuation_stay():
    """digits, commas and dashes don't move"""
    out = scramble("Order 12345 -- arriving tomorrow, maybe!", 3)
    assert out.startswith("O") and "12345 --" in out and out.endswith("e!")
