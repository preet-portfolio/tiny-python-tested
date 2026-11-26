#!/usr/bin/env python3
"""Twelve Days of Christmas: sing the song up to a given day."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Twelve Days of Christmas")
    parser.add_argument("-n", "--num", type=int, default=12, help="Number of days to sing")
    parser.add_argument("-o", "--outfile", default=None, help="Outfile (default: STDOUT)")
    return parser.parse_args()


def verse(day):
    """One verse: the day's line, then every gift from today back to the first."""
    return ""


def main():
    """Sing to the screen or into a file."""
    args = get_args()
    # Your turn: the tests say what the song should look like.
    print(verse(args.num))


if __name__ == "__main__":
    main()
