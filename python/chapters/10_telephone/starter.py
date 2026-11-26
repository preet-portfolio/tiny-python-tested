#!/usr/bin/env python3
"""Telephone: pass a message along."""

import argparse
import os
import random


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Telephone")
    parser.add_argument("text", help="Input text or file")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    parser.add_argument("-m", "--mutations", type=float, default=0.1, help="Percent mutations")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def main():
    """Say it, and hear it."""
    args = get_args()
    random.seed(args.seed)
    # Your turn: check --mutations, then change that share of the characters.
    print(f'You said: "{args.text}"')


if __name__ == "__main__":
    main()
