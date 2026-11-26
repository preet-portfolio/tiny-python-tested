"""Real-world cases for twelve_days.py: the song file is a snapshot.

The author's tests compare after .rstrip(), so a file that loses its last line ending still
passes. A golden-file (snapshot) test compares byte for byte, the way `diff` and `wc -l` do.
"""

import os
from subprocess import getstatusoutput

prg = "./twelve_days.py"


def sing_to_file(n: int) -> str:
    name = f"snapshot-{n}.txt"
    try:
        rv, out = getstatusoutput(f"{prg} -n {n} -o {name}")
        assert rv == 0 and out == ""
        with open(name, encoding="utf-8", newline="") as fh:
            return fh.read()
    finally:
        if os.path.exists(name):
            os.remove(name)


def test_matches_snapshot_byte_for_byte():
    """the whole song file is exactly the golden file, last line ending included"""
    for n in (1, 2, 12):
        with open(f"test-out/{n}.out", encoding="utf-8", newline="") as fh:
            assert sing_to_file(n) == fh.read()


def test_wc_counts_113_lines():
    """`wc -l` counts line endings: the full song has 113 of them"""
    assert sing_to_file(12).count("\n") == 113


def test_file_ends_with_exactly_one_newline():
    """the file ends with one line ending: not none, not a blank line"""
    for n in (1, 5, 12):
        text = sing_to_file(n)
        assert text.endswith("\n") and not text.endswith("\n\n")


def test_each_day_adds_one_gift():
    """verse n names n gifts, newest first, ending with the partridge"""
    verses = sing_to_file(12).rstrip("\n").split("\n\n")
    assert len(verses) == 12
    for n, verse in enumerate(verses, start=1):
        lines = verse.split("\n")
        assert len(lines) == n + 2
        assert lines[-1].endswith("partridge in a pear tree.")


def test_shorter_song_is_the_start_of_the_longer():
    """singing 5 days gives exactly the first 5 verses of the 12-day song"""
    full = sing_to_file(12)
    for n in (3, 5, 11):
        assert full.startswith(sing_to_file(n))


def test_only_days_1_to_12():
    """day 0 and day 13 are refused; day 1 and day 12 are fine"""
    for n in (0, 13):
        rv, out = getstatusoutput(f"{prg} -n {n}")
        assert rv != 0
        assert f'--num "{n}" must be between 1 and 12' in out
    for n in (1, 12):
        rv, _ = getstatusoutput(f"{prg} -n {n}")
        assert rv == 0
