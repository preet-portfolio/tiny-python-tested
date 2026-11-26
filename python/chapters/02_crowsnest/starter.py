#!/usr/bin/env python3
"""Crow's Nest: announce what the lookout sees."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Crow's Nest -- choose the correct article")
    parser.add_argument("word", help="A word")
    return parser.parse_args()


def main():
    """Print the lookout's call."""
    word = get_args().word
    # Your turn: the tests expect a sentence. Run them to see which one.
    print(word)


if __name__ == "__main__":
    main()
