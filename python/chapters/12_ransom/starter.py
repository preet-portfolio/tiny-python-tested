#!/usr/bin/env python3
"""Ransom note: randomly capitalize text."""

import argparse
import os
import random


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Ransom Note")
    parser.add_argument("text", help="Input text or file")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def main():
    """Print the note."""
    args = get_args()
    random.seed(args.seed)
    print(args.text)


if __name__ == "__main__":
    main()
