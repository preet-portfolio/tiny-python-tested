#!/usr/bin/env python3
"""Rhymer, the book's way: one regex splits off the leading consonants."""

import argparse
import re
import string

VOWELS = "aeiou"
CONSONANTS = [c for c in string.ascii_lowercase if c not in VOWELS]
CLUSTERS = [
    "bl", "br", "ch", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "sc", "sh", "sk",
    "sl", "sm", "sn", "sp", "st", "sw", "th", "tr", "tw", "thw", "wh", "wr", "sch", "scr",
    "shr", "sph", "spl", "spr", "squ", "str", "thr",
]
SOUNDS = sorted(CONSONANTS + CLUSTERS)


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description='Make rhyming "words"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("word", metavar="word", help="A word to rhyme")
    return parser.parse_args()


def stemmer(word: str) -> tuple[str, str]:
    """(leading consonants, rest) of the lower-cased word."""
    word = word.lower()
    match = re.match(f"([{''.join(CONSONANTS)}]+)?([{VOWELS}])(.*)", word)
    if match:
        start, vowel, rest = match.groups()
        return start or "", vowel + rest
    return word, ""


def main() -> None:
    """Print the rhymes, or say the word can't be rhymed."""
    word = get_args().word
    start, rest = stemmer(word)
    if rest:
        print("\n".join(sound + rest for sound in SOUNDS if sound != start))
    else:
        print(f'Cannot rhyme "{word}"')


if __name__ == "__main__":
    main()
