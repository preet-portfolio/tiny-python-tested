#!/usr/bin/env python3
"""Scrambler: shuffle the middle letters of every word, keeping the first and last."""

import argparse
import os
import random
import re

# A word is letters (any alphabet, accents too), with apostrophes allowed inside: "Don't".
LETTER = r"[^\W\d_]"
WORD = re.compile(f"({LETTER}(?:(?:{LETTER}|')*{LETTER})?)")


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
    """Shuffle the middle of a word of four or more letters.

    ALL-CAPS words are acronyms (NASA, HTML): scrambled, nobody can read them, so they stay.
    """
    if len(word) <= 3 or word.isupper():
        return word
    middle = list(word[1:-1])
    random.shuffle(middle)
    return word[0] + "".join(middle) + word[-1]


def scramble_line(line: str) -> str:
    """Scramble the words of one line; spaces and punctuation stay where they are."""
    return "".join(scramble(part) if i % 2 else part for i, part in enumerate(WORD.split(line)))


def main() -> None:
    """Print the scrambled text, line by line."""
    args = get_args()
    random.seed(args.seed)
    for line in args.text.splitlines():
        print(scramble_line(line))


if __name__ == "__main__":
    main()
