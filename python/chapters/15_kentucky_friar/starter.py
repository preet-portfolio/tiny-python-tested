#!/usr/bin/env python3
"""Kentucky Friar: give text a Southern lilt."""

import argparse
import os


def get_args():
    """Parse the command line; a text argument that names a file is read."""
    parser = argparse.ArgumentParser(description="Southern fry text")
    parser.add_argument("text", help="Input text or file")
    args = parser.parse_args()
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as fh:
            args.text = fh.read()
    return args


def fry(word):
    """Change one word: "you" and two-syllable "-ing" words get the treatment."""
    return word


def main():
    """Fry every line, word by word."""
    for line in get_args().text.splitlines():
        print(line)


if __name__ == "__main__":
    main()
