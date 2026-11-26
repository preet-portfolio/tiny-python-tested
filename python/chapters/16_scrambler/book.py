#!/usr/bin/env python3
"""Scrambler, the book's way: a regex for English words, then shuffle each middle."""

import argparse
import os
import random
import re

WORD = re.compile("([a-zA-Z](?:[a-zA-Z']*[a-zA-Z])?)")


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Scramble the letters of words",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def scramble(word: str) -> str:
    """Shuffle the middle of a word of four or more letters."""
    if len(word) > 3 and re.match(r"\w+", word):
        middle = list(word[1:-1])
        random.shuffle(middle)
        return word[0] + "".join(middle) + word[-1]
    return word


def scramble_line(line: str) -> str:
    """Scramble every piece the regex splits out."""
    return "".join(map(scramble, WORD.split(line)))


def main() -> None:
    """Print the scrambled text, line by line."""
    args = get_args()
    random.seed(args.seed)
    for line in args.text.splitlines():
        print(scramble_line(line))


if __name__ == "__main__":
    main()
