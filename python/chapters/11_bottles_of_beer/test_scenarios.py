"""Real-world cases for bottles.py: the song as product copy.

"1 item left", "No more items", "21 items left": plural rules break at the edges, and the
book's examples only cover 1 and 2 bottles end to end.
"""

import re
from subprocess import getstatusoutput

prg = "./bottles.py"


def sing(args: str = "") -> list[str]:
    rv, out = getstatusoutput(f"{prg} {args}".strip())
    assert rv == 0
    return out.split("\n\n")


def test_default_is_ten_verses():
    """no flag sings ten verses, starting at 10"""
    verses = sing()
    assert len(verses) == 10
    assert verses[0].startswith("10 bottles of beer on the wall,")


def test_one_verse_per_bottle():
    """-n 99 sings 99 verses, one blank line between each"""
    verses = sing("-n 99")
    assert len(verses) == 99
    assert all(len(v.splitlines()) == 4 for v in verses)


def test_numbers_ending_in_one_stay_plural():
    """21, 11 and 101 are plural; only 1 is singular"""
    text = "\n".join(sing("-n 101"))
    for n in (101, 21, 11):
        assert f"{n} bottles of beer," in text
    assert not re.search(r"(?<!\d)1 bottles", text)


def test_ends_with_no_more():
    """the song ends on 'No more bottles', never '0 bottles'"""
    verses = sing("-n 3")
    assert verses[-1].endswith("No more bottles of beer on the wall!")
    assert "0 bottles" not in "\n".join(verses)
