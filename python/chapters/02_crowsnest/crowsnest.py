#!/usr/bin/env python3
"""Crow's Nest: announce what the lookout sees, with the right article."""

import argparse
import re

VOWELS = frozenset("aeiou")

# English picks the article by sound, not spelling. These prefixes are the common
# exceptions to "vowel letter means 'an'".
SOUNDS_LIKE_VOWEL = ("hour", "honest", "honor", "honour", "heir")
SOUNDS_LIKE_CONSONANT = ("uni", "use", "usu", "uti", "eu", "ewe", "one", "once")

# Letter names that start with a vowel sound: "an F", "an M", "an X".
VOWEL_LETTER_NAMES = frozenset("AEFHILMNORSX")


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Crow's Nest -- choose the correct article",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("word", metavar="word", help="A word")
    return parser.parse_args()


def _number_article(digits: str) -> str:
    """'an' for numbers said starting with 'eight' or 'eleven'/'eighteen'."""
    if digits.startswith("8"):
        return "an"
    if digits[:2] in ("11", "18") and len(digits) % 3 == 2:
        return "an"
    return "a"


def article_for(word: str) -> str:
    """Return the article a careful speaker would use before ``word``."""
    if not word:
        return "a"
    leading_digits = re.match(r"\d+", word)
    if leading_digits:
        return _number_article(leading_digits.group())
    if word.isupper() and len(word) <= 4:
        return "an" if word[0] in VOWEL_LETTER_NAMES else "a"
    lower = word.lower()
    if lower.startswith(SOUNDS_LIKE_VOWEL):
        return "an"
    if lower.startswith(SOUNDS_LIKE_CONSONANT):
        return "a"
    return "an" if lower[0] in VOWELS else "a"


def main() -> None:
    """Print the lookout's call."""
    word = get_args().word
    print(f"Ahoy, Captain, {article_for(word)} {word} off the larboard bow!")


if __name__ == "__main__":
    main()
