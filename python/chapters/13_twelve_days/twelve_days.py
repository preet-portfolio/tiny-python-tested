#!/usr/bin/env python3
"""Twelve Days of Christmas: sing the song up to a given day."""

import argparse
import sys

ORDINALS = (
    "first", "second", "third", "fourth", "fifth", "sixth",
    "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
)
GIFTS = (
    "A partridge in a pear tree.",
    "Two turtle doves,",
    "Three French hens,",
    "Four calling birds,",
    "Five gold rings,",
    "Six geese a laying,",
    "Seven swans a swimming,",
    "Eight maids a milking,",
    "Nine ladies dancing,",
    "Ten lords a leaping,",
    "Eleven pipers piping,",
    "Twelve drummers drumming,",
)


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Twelve Days of Christmas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-n", "--num", metavar="days", type=int, default=12,
                        help="Number of days to sing")
    parser.add_argument("-o", "--outfile", metavar="FILE", default=None,
                        help="Outfile (default: STDOUT)")
    args = parser.parse_args()
    if not 1 <= args.num <= 12:
        parser.error(f'--num "{args.num}" must be between 1 and 12')
    return args


def verse(day: int) -> str:
    """One verse: the day's line, then every gift from today back to the first."""
    gifts = [GIFTS[i] for i in range(day - 1, -1, -1)]
    if day > 1:
        gifts[-1] = "And a" + gifts[-1][1:]
    return "\n".join([f"On the {ORDINALS[day - 1]} day of Christmas,",
                      "My true love gave to me,", *gifts])


def song(num: int) -> str:
    """Every verse from day one to ``num``, a blank line between, one newline at the end."""
    return "\n\n".join(verse(day) for day in range(1, num + 1)) + "\n"


def main() -> None:
    """Sing to the screen or into a file."""
    args = get_args()
    text = song(args.num)
    if args.outfile is None:
        sys.stdout.write(text)
        return
    with open(args.outfile, "w", encoding="utf-8", newline="\n") as out:
        out.write(text)


if __name__ == "__main__":
    main()
