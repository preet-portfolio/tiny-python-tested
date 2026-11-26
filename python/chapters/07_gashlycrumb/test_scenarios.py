"""Real-world cases for gashlycrumb.py: a lookup table read from a file.

The same program reads any alphabet file, the NATO phonetic alphabet included. Files people
edit by hand have comments, indentation, blank lines, Windows line endings and, from Notepad,
an invisible mark at the very start. Every case here must pass without breaking a single test
in the author's test.py.
"""

import os
from subprocess import getstatusoutput

prg = "./gashlycrumb.py"
NATO = "Alfa\nBravo\nCharlie\nDelta\nEcho\nFoxtrot\n"


def lookup(table: bytes, letters: str) -> str:
    with open("table.txt", "wb") as fh:
        fh.write(table)
    try:
        rv, out = getstatusoutput(f"{prg} -f table.txt {letters}")
        assert rv == 0, out
        return out
    finally:
        os.remove("table.txt")


def test_nato_alphabet():
    """any alphabet file works, and unknown letters are reported"""
    assert lookup(NATO.encode(), "a F z") == 'Alfa\nFoxtrot\nI do not know "z".'


def test_notepad_mark_is_ignored():
    """the first line still counts when Notepad hid a mark before it"""
    assert lookup(("﻿" + NATO).encode(), "a b") == "Alfa\nBravo"


def test_indented_lines():
    """spaces or tabs before a line don't hide it"""
    assert lookup(b"  Alfa\n\tBravo\n", "a b") == "Alfa\nBravo"


def test_comments_are_not_entries():
    """a '# comment' line is a note for people, not an entry"""
    table = b"# The NATO alphabet\nAlfa\nBravo\n"
    assert lookup(table, "a '#'") == 'Alfa\nI do not know "#".'


def test_blank_lines_are_ignored():
    """empty lines between entries don't break anything"""
    assert lookup(b"Alfa\n\n\nBravo\n\n", "b a") == "Bravo\nAlfa"


def test_windows_line_endings():
    """lines ending in \\r\\n give clean answers"""
    assert lookup(b"Alfa\r\nBravo\r\n", "a b") == "Alfa\nBravo"


def test_table_from_a_pipe():
    """'-f -' reads the table from a pipe"""
    rv, out = getstatusoutput(f"{prg} -f - q < alternate.txt")
    assert rv == 0
    assert out == "Q is for Quintanna, flayed in the night."
