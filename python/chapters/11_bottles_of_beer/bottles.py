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
    # The book's song is about beer, and its tests check that word for word; the site sings
    # about lemonade instead by passing --drink.
    parser.add_argument("-d", "--drink", metavar="drink", default="beer", help="What's in the bottles")
    args = parser.parse_args()
    if args.num < 1:
        parser.error(f'--num "{args.num}" must be greater than 0')
    return args


def bottles(n: int) -> str:
    """'1 bottle', '2 bottles', and 'No more bottles' for zero."""
    if n == 0:
        return "No more bottles"
    return f"{n} bottle{'' if n == 1 else 's'}"


def verse(n: int, drink: str) -> str:
    """One verse, starting with n bottles of drink on the wall."""
    return "\n".join(
        [
            f"{bottles(n)} of {drink} on the wall,",
            f"{bottles(n)} of {drink},",
            "Take one down, pass it around,",
            f"{bottles(n - 1)} of {drink} on the wall!",
        ]
    )


def main() -> None:
    """Sing every verse from --num down to 1."""
    args = get_args()
    print("\n\n".join(verse(n, args.drink) for n in range(args.num, 0, -1)))


if __name__ == "__main__":
    main()
