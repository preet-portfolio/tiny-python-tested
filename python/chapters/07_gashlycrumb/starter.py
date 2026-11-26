#!/usr/bin/env python3
"""Gashlycrumb: look up the line for each letter."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Gashlycrumb")
    parser.add_argument("letter", nargs="+", help="Letter(s)")
    parser.add_argument("-f", "--file", default="gashlycrumb.txt", help="Input file")
    return parser.parse_args()


def main():
    """Print the line for each letter, or say we don't know it."""
    args = get_args()
    # Your turn: read args.file into a dictionary keyed by each line's first letter.
    for letter in args.letter:
        print(letter)


if __name__ == "__main__":
    main()
