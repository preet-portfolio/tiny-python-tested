#!/usr/bin/env python3
"""Howler: SHOUT the text."""

import argparse
import os


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Howler (upper-cases input)")
    parser.add_argument("text", help="Input string or file")
    parser.add_argument("-o", "--outfile", default="", help="Output filename")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read().rstrip()
    return args


def main():
    """Shout to STDOUT, or into --outfile."""
    args = get_args()
    # Your turn: shout it, and write it to args.outfile when there is one.
    print(args.text)


if __name__ == "__main__":
    main()
