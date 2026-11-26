#!/usr/bin/env python3
"""Apples and Bananas: swap every vowel for one vowel."""

import argparse
import os


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Apples and bananas")
    parser.add_argument("text", help="Input text or file")
    parser.add_argument("-v", "--vowel", default="a", help="The vowel to substitute")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def main():
    """Print the song."""
    args = get_args()
    # Your turn: every a, e, i, o and u becomes args.vowel (capitals stay capitals).
    print(args.text)


if __name__ == "__main__":
    main()
