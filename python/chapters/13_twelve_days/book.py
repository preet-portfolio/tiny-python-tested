#!/usr/bin/env python3
"""Twelve Days of Christmas, the book's way: join the verses and write them out."""

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
    parser.add_argument("-o", "--outfile", metavar="FILE", type=argparse.FileType("wt"),
                        default=None, help="Outfile (default: STDOUT)")
    args = parser.parse_args()
    if not 1 <= args.num <= 12:
        parser.error(f'--num "{args.num}" must be between 1 and 12')
    return args


def verse(day: int) -> str:
    """One verse."""
    gifts = list(reversed(GIFTS[:day]))
    if day > 1:
        gifts[-1] = "And a" + gifts[-1][1:]
    return "\n".join([f"On the {ORDINALS[day - 1]} day of Christmas,",
                      "My true love gave to me,", *gifts])


def main() -> None:
    """Join the verses with blank lines and write them."""
    args = get_args()
    out = args.outfile or sys.stdout
    out.write("\n\n".join(verse(day) for day in range(1, args.num + 1)))


if __name__ == "__main__":
    main()
