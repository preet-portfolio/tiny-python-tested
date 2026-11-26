#!/usr/bin/env python3
"""Jump the Five: swap each digit for its partner across the 5 on a phone keypad."""

import argparse
import unicodedata

# 1<->9, 2<->8, 3<->7, 4<->6 and 5<->0, as digit values.
PARTNER = {1: 9, 2: 8, 3: 7, 4: 6, 5: 0, 6: 4, 7: 3, 8: 2, 9: 1, 0: 5}


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Jump the Five",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="str", help="Input text")
    return parser.parse_args()


def jump(char: str) -> str:
    """Jump one character. Any script's digits jump, and stay in that script."""
    if not char.isdecimal():
        return char
    value = unicodedata.decimal(char)
    # Unicode keeps each script's digits 0-9 together, so its zero is value places back.
    return chr(ord(char) - value + PARTNER[value])


def main() -> None:
    """Print the text with every digit jumped."""
    print("".join(jump(c) for c in get_args().text))


if __name__ == "__main__":
    main()
