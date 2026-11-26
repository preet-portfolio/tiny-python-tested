#!/usr/bin/env python3
"""Picnic: say what you're bringing, as a tidy English list."""

import argparse
import unicodedata


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Picnic game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("item", metavar="str", nargs="+", help="Item(s) to bring")
    parser.add_argument("-s", "--sorted", action="store_true", help="Sort the items")
    args = parser.parse_args()
    args.item = clean(args.item)
    if not args.item:
        parser.error("Nothing to bring: every item was blank")
    return args


def clean(items: list[str]) -> list[str]:
    """Trim spaces, drop blanks and drop repeats (ignoring capitals), keeping the order."""
    seen: set[str] = set()
    out = []
    for raw in items:
        item = " ".join(raw.split())
        key = item.casefold()
        if item and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def sort_key(item: str) -> str:
    """Dictionary order: capitals and accents don't move an item."""
    plain = unicodedata.normalize("NFKD", item)
    return "".join(c for c in plain if not unicodedata.combining(c)).casefold()


def join_items(items: list[str]) -> str:
    """'a', 'a and b', or 'a, b, and c' (semicolons if an item has its own comma)."""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    sep = "; " if any("," in item for item in items) else ", "
    return sep.join(items[:-1]) + f"{sep}and {items[-1]}"


def main() -> None:
    """Print what we're bringing."""
    args = get_args()
    items = sorted(args.item, key=sort_key) if args.sorted else args.item
    print(f"You are bringing {join_items(items)}.")


if __name__ == "__main__":
    main()
