#!/usr/bin/env python3
"""Telephone: pass a message along and hear it come back a little wrong."""

import argparse
import os
import random
import string

# Every character a "mistake" can turn into, in a fixed order so a seed means one message.
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


def how_many(length: int, rate: float) -> int:
    """Mistakes to make: rate x length, rounded, but at least one if any are asked for."""
    if length == 0 or rate == 0:
        return 0
    return max(1, round(length * rate))


def mutate(text: str, rate: float) -> str:
    """Change ``rate`` of the characters to different ones. Line breaks stay put."""
    places = [i for i, c in enumerate(text) if c != "\n"]
    chars = list(text)
    for i in random.sample(places, how_many(len(places), rate)):
        chars[i] = random.choice(ALPHA.replace(chars[i], ""))
    return "".join(chars)


def main() -> None:
    """Say it, and hear it."""
    args = get_args()
    random.seed(args.seed)
    print(f'You said: "{args.text}"\nI heard : "{mutate(args.text, args.mutations)}"')


if __name__ == "__main__":
    main()
