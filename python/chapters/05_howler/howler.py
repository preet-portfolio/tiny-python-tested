#!/usr/bin/env python3
"""Howler: SHOUT the text, from the command line, a file or a pipe."""

import argparse
import os
import sys


def get_args() -> argparse.Namespace:
    """Parse the command line. The text may name a file, or be '-' to read a pipe."""
    parser = argparse.ArgumentParser(
        description="Howler (upper-cases input)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", metavar="text", help="Input string or file ('-' reads STDIN)")
    parser.add_argument("-o", "--outfile", metavar="str", default="", help="Output filename")
    args = parser.parse_args()
    args.text = read_input(args.text)
    return args


def read_input(text: str) -> str:
    """The text itself, the contents of the file it names, or STDIN for '-'."""
    if text == "-":
        text = sys.stdin.read()
    elif os.path.isfile(text):
        with open(text, encoding="utf-8") as fh:
            text = fh.read()
    # Windows Notepad starts files with an invisible byte-order mark; it isn't text.
    return text.removeprefix("﻿").rstrip()


def main() -> None:
    """Shout to STDOUT, or into --outfile."""
    args = get_args()
    shout = args.text.upper() + "\n"
    if not args.outfile:
        sys.stdout.write(shout)
        return
    try:
        with open(args.outfile, "w", encoding="utf-8") as fh:
            fh.write(shout)
    except OSError as err:
        sys.exit(f"howler.py: can't write '{args.outfile}': {err.strerror}")


if __name__ == "__main__":
    main()
