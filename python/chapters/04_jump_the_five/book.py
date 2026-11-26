#!/usr/bin/env python3
"""Jump the Five, the book's way: a dictionary from '1' to '9' and so on."""

import argparse

JUMPER = {"1": "9", "2": "8", "3": "7", "4": "6", "5": "0",
          "6": "4", "7": "3", "8": "2", "9": "1", "0": "5"}


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Jump the Five",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="str", help="Input text")
    return parser.parse_args()


def main() -> None:
    """Print the text with every digit jumped."""
    print("".join(JUMPER.get(c, c) for c in get_args().text))


if __name__ == "__main__":
    main()
