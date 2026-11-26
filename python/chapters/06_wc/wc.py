#!/usr/bin/env python3
"""Words count: lines, words and bytes, the way Unix wc counts them."""

import argparse
import sys
from typing import BinaryIO


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Emulate wc (word count)")
    parser.add_argument("file", metavar="FILE", nargs="*", help="Input file(s); none reads STDIN")
    return parser.parse_args()


def count(fh: BinaryIO) -> tuple[int, int, int]:
    """Newlines, whitespace-separated words and bytes, as wc reports them.

    Bytes, not characters: 'café' is five bytes in UTF-8. Lines are newline characters,
    so a last line with no newline isn't counted, exactly as wc does.
    """
    data = fh.read()
    return data.count(b"\n"), len(data.split()), len(data)


def row(counts: tuple[int, int, int], name: str) -> str:
    """Three right-aligned columns, eight wide, then the name."""
    return "".join(f"{n:8}" for n in counts) + f" {name}"


def main() -> None:
    """Count each input, then a total when there's more than one."""
    names = get_args().file
    totals = [0, 0, 0]
    failed = False
    if not names:
        print(row(count(sys.stdin.buffer), "<stdin>"))
        return
    for name in names:
        try:
            with open(name, "rb") as fh:
                counts = count(fh)
        except OSError as err:
            # Like wc: report it, keep counting the rest, exit non-zero at the end.
            print(f"wc.py: {err}", file=sys.stderr)
            failed = True
            continue
        totals = [t + c for t, c in zip(totals, counts)]
        print(row(counts, name))
    if len(names) > 1:
        print(row((totals[0], totals[1], totals[2]), "total"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
