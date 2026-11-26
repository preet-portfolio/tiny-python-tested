#!/usr/bin/env python3
"""Howler, the book's way: the text or the file it names, upper-cased."""

import argparse
import os


def get_args() -> argparse.Namespace:
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(
        description="Howler (upper-cases input)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input string or file")
    parser.add_argument("-o", "--outfile", metavar="str", default="", help="Output filename")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text) as fh:
            args.text = fh.read().rstrip()
    return args


def main() -> None:
    """Shout to STDOUT, or into --outfile."""
    args = get_args()
    if args.outfile:
        with open(args.outfile, "wt") as out_fh:
            out_fh.write(args.text.upper() + "\n")
    else:
        print(args.text.upper())


if __name__ == "__main__":
    main()
