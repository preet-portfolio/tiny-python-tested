#!/usr/bin/env python3
"""Gashlycrumb: look up the line for each letter in an alphabet file."""

import argparse
import sys
from collections.abc import Iterable


def get_args() -> argparse.Namespace:
    """Parse the command line and read the lookup table."""
    parser = argparse.ArgumentParser(
        description="Gashlycrumb",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("letter", metavar="letter", nargs="+", help="Letter(s)")
    parser.add_argument(
        "-f", "--file", metavar="FILE", default="gashlycrumb.txt",
        help="Input file ('-' reads STDIN)",
    )
    args = parser.parse_args()
    try:
        if args.file == "-":
            args.table = read_table(sys.stdin)
        else:
            with open(args.file, encoding="utf-8") as fh:
                args.table = read_table(fh)
    except OSError as err:
        parser.error(f"can't open '{args.file}': {err}")
    return args


def read_table(lines: Iterable[str]) -> dict[str, str]:
    """Map each line's first letter (in capitals) to the line.

    Like a config file: surrounding spaces, blank lines, '#' comments and the invisible
    mark Windows Notepad puts at the start of a file are not entries.
    """
    table: dict[str, str] = {}
    for raw in lines:
        line = raw.removeprefix("﻿").strip()
        if line and not line.startswith("#"):
            table[line[0].upper()] = line
    return table


def main() -> None:
    """Print the line for each letter, or say we don't know it."""
    args = get_args()
    for letter in args.letter:
        print(args.table.get(letter.upper(), f'I do not know "{letter}".'))


if __name__ == "__main__":
    main()
