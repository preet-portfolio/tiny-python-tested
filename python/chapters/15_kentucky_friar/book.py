#!/usr/bin/env python3
"""Kentucky Friar, the book's way: split on non-word characters and fry each piece."""

import argparse
import os
import re


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Southern fry text",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def fry(word: str) -> str:
    """'you' -> "y'all"; a two-syllable '-ing' word drops its g."""
    if word.lower() == "you":
        return word[0] + "'all"
    if word.endswith("ing") and re.search("[aeiouy]", word[:-3], re.IGNORECASE):
        return word[:-1] + "'"
    return word


def main() -> None:
    """Fry each line, word by word."""
    for line in get_args().text.splitlines():
        print("".join(map(fry, re.split(r"(\W+)", line))))


if __name__ == "__main__":
    main()
