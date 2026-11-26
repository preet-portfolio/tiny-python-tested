#!/usr/bin/env python3
"""Apples and Bananas: sing the text with every vowel swapped for one vowel."""

import argparse
import os
import unicodedata

VOWELS = "aeiou"


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Apples and bananas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    parser.add_argument(
        "-v", "--vowel", metavar="vowel", type=str.lower, default="a",
        choices=list(VOWELS), help="The vowel to substitute",
    )
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def swap(char: str, vowel: str) -> str:
    """The new vowel if ``char`` is a vowel (accented or not), keeping its case."""
    base = unicodedata.normalize("NFD", char)[0]
    if base.lower() not in VOWELS:
        return char
    return vowel.upper() if base.isupper() else vowel


def sing(text: str, vowel: str) -> str:
    """The whole text, sung with one vowel."""
    return "".join(swap(c, vowel) for c in unicodedata.normalize("NFC", text))


def main() -> None:
    """Print the song."""
    args = get_args()
    print(sing(args.text, args.vowel))


if __name__ == "__main__":
    main()
