#!/usr/bin/env python3
"""Gashlycrumb, the book's way: the first character of each line is its key."""

import argparse


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Gashlycrumb",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("letter", metavar="letter", nargs="+", help="Letter(s)")
    parser.add_argument(
        "-f", "--file", metavar="FILE", type=argparse.FileType("rt"),
        default="gashlycrumb.txt", help="Input file",
    )
    return parser.parse_args()


def main() -> None:
    """Print the line for each letter, or say we don't know it."""
    args = get_args()
    lookup = {line[0].upper(): line.rstrip() for line in args.file}
    for letter in args.letter:
        if letter.upper() in lookup:
            print(lookup[letter.upper()])
        else:
            print(f'I do not know "{letter}".')


if __name__ == "__main__":
    main()
