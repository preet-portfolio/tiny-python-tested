#!/usr/bin/env python3
"""Mad Libs, the book's way: findall the placeholders, re.sub each answer in."""

import argparse
import re
import sys


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Mad Libs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"),
                        help="Input file")
    parser.add_argument("-i", "--inputs", metavar="input", nargs="*", default=None,
                        help="Inputs (for testing)")
    return parser.parse_args()


def main() -> None:
    """Ask for (or take) one word per placeholder and substitute it."""
    args = get_args()
    inputs = args.inputs
    text = args.file.read().rstrip()
    blanks = re.findall("(<([^<>]+)>)", text)
    if not blanks:
        sys.exit(f'"{args.file.name}" has no placeholders.')
    for placeholder, name in blanks:
        article = "an" if name.lower()[0] in "aeiou" else "a"
        answer = inputs.pop(0) if inputs else input(f"Give me {article} {name}: ")
        text = re.sub(placeholder, answer, text, count=1)
    print(text)


if __name__ == "__main__":
    main()
