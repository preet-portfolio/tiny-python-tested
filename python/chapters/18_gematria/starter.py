#!/usr/bin/env python3
"""Gematria: turn each word into a number."""

import argparse
import os


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Gematria")
    parser.add_argument("text", help="Input text or file")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def word2num(word):
    """Add up the codes of the word's letters."""
    return 0


def main():
    """Print one line of numbers per line of text."""
    for line in get_args().text.splitlines():
        print(line)


if __name__ == "__main__":
    main()
