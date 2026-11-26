#!/usr/bin/env python3
"""Crow's Nest, the book's rule only: a vowel letter means 'an'."""

import argparse


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Crow's Nest -- choose the correct article")
    parser.add_argument("word", metavar="word", help="A word")
    return parser.parse_args()


def main() -> None:
    """Print the lookout's call."""
    word = get_args().word
    article = "an" if word[0].lower() in "aeiou" else "a"
    print(f"Ahoy, Captain, {article} {word} off the larboard bow!")


if __name__ == "__main__":
    main()
