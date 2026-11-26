#!/usr/bin/env python3
"""Ransom note, the book's way: flip a coin per character and trust .upper()."""

import argparse
import os
import random


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Ransom Note",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    parser.add_argument("-s", "--seed", metavar="int", type=int, default=None, help="Random seed")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def choose(char: str) -> str:
    """Flip a coin: upper case on heads, lower case on tails.

    One coin flip per character, so a seed means the same note.
    """
    return char.upper() if random.choice([False, True]) else char.lower()


def ransom(text: str) -> str:
    """The whole note."""
    return "".join(choose(c) for c in text)


def main() -> None:
    """Print the note."""
    args = get_args()
    random.seed(args.seed)
    print(ransom(args.text))


if __name__ == "__main__":
    main()
