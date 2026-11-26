#!/usr/bin/env python3
"""Scrambler: shuffle the middle letters of every word."""

import argparse
import os
import random


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Scramble the letters of words")
    parser.add_argument("text", help="Input text or file")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def scramble(word):
    """Shuffle the middle of one word."""
    return word


def scramble_line(line):
    """Scramble the words of one line."""
    return line


def main():
    """Print the scrambled text, line by line."""
    args = get_args()
    random.seed(args.seed)
    for line in args.text.splitlines():
        print(scramble_line(line))


if __name__ == "__main__":
    main()
