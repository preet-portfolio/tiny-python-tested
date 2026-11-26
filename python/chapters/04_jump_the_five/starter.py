#!/usr/bin/env python3
"""Jump the Five: swap each digit for its partner across the 5."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Jump the Five")
    parser.add_argument("text", metavar="str", help="Input text")
    return parser.parse_args()


def main():
    """Print the text with every digit jumped."""
    text = get_args().text
    # Your turn: 1 becomes 9, 2 becomes 8 ... and 5 and 0 swap.
    print(text)


if __name__ == "__main__":
    main()
