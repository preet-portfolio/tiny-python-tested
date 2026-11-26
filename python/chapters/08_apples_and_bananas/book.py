#!/usr/bin/env python3
"""Apples and Bananas, the book's way: str.replace for each vowel."""

import argparse
import os


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Apples and bananas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    parser.add_argument(
        "-v", "--vowel", metavar="vowel", default="a",
        choices=list("aeiou"), help="The vowel to substitute",
    )
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def main() -> None:
    """Print the song."""
    args = get_args()
    text = args.text
    for v in "aeiou":
        text = text.replace(v, args.vowel).replace(v.upper(), args.vowel.upper())
    print(text)


if __name__ == "__main__":
    main()
