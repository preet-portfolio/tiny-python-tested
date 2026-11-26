#!/usr/bin/env python3
"""Gematria: turn each word into a number by adding up its letters' codes."""

import argparse
import os
import re
import unicodedata


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Gematria",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def clean(word: str) -> str:
    """Keep A-Z, a-z and 0-9; an accented letter counts as its plain letter (é -> e)."""
    plain = unicodedata.normalize("NFKD", word)
    return re.sub("[^A-Za-z0-9]", "", plain)


def word2num(word: str) -> int | None:
    """The sum of the character codes, or None if nothing countable is left."""
    kept = clean(word)
    return sum(map(ord, kept)) if kept else None


def encode_line(line: str) -> str:
    """Every word on the line as a number; pieces with nothing to count are skipped."""
    nums = (word2num(word) for word in line.split())
    return " ".join(str(n) for n in nums if n is not None)


def main() -> None:
    """Print one line of numbers per line of text."""
    for line in get_args().text.splitlines():
        print(encode_line(line))


if __name__ == "__main__":
    main()
