#!/usr/bin/env python3
"""Telephone, the book's way: round(rate x length) random positions get a new character."""

import argparse
import os
import random
import string

ALPHA = "".join(sorted(string.ascii_letters + string.punctuation))


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Telephone",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input text or file")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("-m", "--mutations", metavar="mutations", type=float, default=0.1,
                        help="Percent mutations")
    args = parser.parse_args()
    if not 0 <= args.mutations <= 1:
        parser.error(f'--mutations "{args.mutations}" must be between 0 and 1')
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def mutate(text: str, rate: float) -> str:
    """Change round(rate x length) characters to different ones."""
    new_text = text
    for i in random.sample(range(len(text)), round(len(text) * rate)):
        new_char = random.choice(ALPHA.replace(new_text[i], ""))
        new_text = new_text[:i] + new_char + new_text[i + 1:]
    return new_text


def main() -> None:
    """Say it, and hear it."""
    args = get_args()
    random.seed(args.seed)
    print(f'You said: "{args.text}"\nI heard : "{mutate(args.text, args.mutations)}"')


if __name__ == "__main__":
    main()
