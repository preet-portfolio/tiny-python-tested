#!/usr/bin/env python3
"""Mad Libs: fill the <placeholders> in a story with your own words."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Mad Libs")
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"), help="Input file")
    parser.add_argument("-i", "--inputs", nargs="*", default=None, help="Inputs (for testing)")
    return parser.parse_args()


def blanks(text):
    """The name of every <blank>, in order."""
    return []


def fill(text, answers):
    """Put each answer into the next blank."""
    return text


def main():
    """Find the blanks, get the answers, print the story."""
    args = get_args()
    text = args.file.read().rstrip()
    print(fill(text, args.inputs or []))


if __name__ == "__main__":
    main()
