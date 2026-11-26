#!/usr/bin/env python3
"""Kentucky Friar: give text a Southern lilt."""

import argparse
import os
import re

# Words are the runs between non-word characters. That splits "you're" into "you", "'"
# and "re", and the book's own Dickinson test expects "y'all're", so it stays that way.
WORD = re.compile(r"(\w+)")


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
    """'you' -> "y'all" and two-syllable '-ing' -> "-in'", keeping the word's case."""
    shouting = word.isupper() and len(word) > 1
    if word.lower() == "you":
        return word[0] + ("'ALL" if shouting else "'all")
    match = re.fullmatch(r"(.+)(ing)", word, re.IGNORECASE)
    if match and re.search("[aeiouy]", match.group(1), re.IGNORECASE):
        return match.group(1) + ("IN'" if shouting else "in'")
    return word


def main() -> None:
    """Fry every word, keeping the lines and everything between the words."""
    text = get_args().text
    for line in text.splitlines():
        print("".join(fry(part) if i % 2 else part for i, part in enumerate(WORD.split(line))))


if __name__ == "__main__":
    main()
