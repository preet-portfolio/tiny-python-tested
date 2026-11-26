#!/usr/bin/env python3
"""Bottles of Beer: sing the countdown from --num to the last bottle."""

import argparse


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Bottles of beer song",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-n", "--num", metavar="number", type=int, default=10, help="How many bottles"
    )
    args = parser.parse_args()
    if args.num < 1:
        parser.error(f'--num "{args.num}" must be greater than 0')
    return args


def bottles(n: int) -> str:
    """'1 bottle', '2 bottles', and 'No more bottles' for zero."""
    if n == 0:
        return "No more bottles"
    return f"{n} bottle{'' if n == 1 else 's'}"


def verse(n: int) -> str:
    """One verse, starting with n bottles on the wall."""
    return "\n".join(
        [
            f"{bottles(n)} of beer on the wall,",
            f"{bottles(n)} of beer,",
            "Take one down, pass it around,",
            f"{bottles(n - 1)} of beer on the wall!",
        ]
    )


def main() -> None:
    """Sing every verse from --num down to 1."""
    num = get_args().num
    print("\n\n".join(verse(n) for n in range(num, 0, -1)))


if __name__ == "__main__":
    main()
