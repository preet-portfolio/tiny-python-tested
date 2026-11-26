#!/usr/bin/env python3
"""Gematria, the book's way: strip to A-Z/0-9 and sum the ord() of what's left."""

import argparse
import os
import re


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


def word2num(word: str) -> str:
    """Sum the character codes of the word's letters and digits."""
    return str(sum(map(ord, re.sub("[^A-Za-z0-9]", "", word))))


def main() -> None:
    """Print one line of numbers per line of text."""
    for line in get_args().text.splitlines():
        print(" ".join(map(word2num, line.split())))


if __name__ == "__main__":
    main()
