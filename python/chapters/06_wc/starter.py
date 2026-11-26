#!/usr/bin/env python3
"""Words count: lines, words and bytes."""

import argparse
import sys


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Emulate wc (word count)")
    parser.add_argument("file", metavar="FILE", nargs="*", help="Input file(s)")
    return parser.parse_args()


def main():
    """Count each input."""
    names = get_args().file
    for name in names:
        with open(name) as fh:
            text = fh.read()
        print(text)


if __name__ == "__main__":
    main()
