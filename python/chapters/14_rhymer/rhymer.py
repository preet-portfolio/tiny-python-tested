#!/usr/bin/env python3
"""Rhymer: swap a word's leading consonant sound for every other one."""

import argparse
import re
import string
import unicodedata

VOWELS = "aeiou"
CONSONANTS = [c for c in string.ascii_lowercase if c not in VOWELS]
CLUSTERS = [
    "bl", "br", "ch", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "sc", "sh", "sk",
    "sl", "sm", "sn", "sp", "st", "sw", "th", "tr", "tw", "thw", "wh", "wr", "sch", "scr",
    "shr", "sph", "spl", "spr", "squ", "str", "thr",
]
# In English a q always brings its u: "quake", never "qake".
SOUNDS = sorted({"qu" if c == "q" else c for c in CONSONANTS} | set(CLUSTERS))


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description='Make rhyming "words"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("word", metavar="word", help="A word to rhyme")
    return parser.parse_args()


def _base(char: str) -> str:
    """The plain letter under an accent: 'é' -> 'e'."""
    return unicodedata.normalize("NFD", char)[0]


def stemmer(word: str) -> tuple[str, str]:
    """Split a lower-cased word into (leading consonant sound, the rest).

    'qu' counts as one sound, and accented vowels count as vowels.
    """
    word = word.strip().lower()
    for i, char in enumerate(word):
        if _base(char) in VOWELS:
            if word[i - 1 : i + 1] == "qu" and i > 0:
                continue
            return word[:i], word[i:]
        if not re.match(r"[a-z]", _base(char)):
            break
    return word, ""


def rhymes(word: str) -> list[str]:
    """Every other sound in front of the word's rest; empty if it can't be rhymed."""
    start, rest = stemmer(word)
    if not rest:
        return []
    return [sound + rest for sound in SOUNDS if sound != start]


def main() -> None:
    """Print the rhymes, or say the word can't be rhymed."""
    word = get_args().word
    found = rhymes(word)
    print("\n".join(found) if found else f'Cannot rhyme "{word}"')


if __name__ == "__main__":
    main()
