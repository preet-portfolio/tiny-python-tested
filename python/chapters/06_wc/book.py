#!/usr/bin/env python3
"""Words count, the book's way: count characters and lines of text."""

import argparse
import sys


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Emulate wc (word count)")
    parser.add_argument("file", metavar="FILE", nargs="*", help="Input file(s)")
    args = parser.parse_args()
    for name in args.file:
        try:
            open(name).close()
        except OSError as err:
            parser.error(f"argument FILE: can't open '{name}': {err}")
    return args


def count(text: str) -> tuple[int, int, int]:
    """Lines, words and characters (the book calls them bytes)."""
    lines = text.splitlines(keepends=True)
    return len(lines), len(text.split()), len(text)


def main() -> None:
    """Count each input, then a total."""
    names = get_args().file
    if not names:
        n = count(sys.stdin.read())
        print(f"{n[0]:8}{n[1]:8}{n[2]:8} <stdin>")
        return
    totals = [0, 0, 0]
    for name in names:
        with open(name, encoding="utf-8") as fh:
            n = count(fh.read())
        totals = [t + c for t, c in zip(totals, n)]
        print(f"{n[0]:8}{n[1]:8}{n[2]:8} {name}")
    if len(names) > 1:
        print(f"{totals[0]:8}{totals[1]:8}{totals[2]:8} total")


if __name__ == "__main__":
    main()
