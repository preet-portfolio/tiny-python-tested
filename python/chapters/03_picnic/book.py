#!/usr/bin/env python3
"""Picnic, the book's way: sort with sorted() and join with commas."""

import argparse


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Picnic game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("item", metavar="str", nargs="+", help="Item(s) to bring")
    parser.add_argument("-s", "--sorted", action="store_true", help="Sort the items")
    return parser.parse_args()


def main() -> None:
    """Print what we're bringing."""
    args = get_args()
    items = sorted(args.item) if args.sorted else args.item
    if len(items) == 1:
        bringing = items[0]
    elif len(items) == 2:
        bringing = " and ".join(items)
    else:
        bringing = ", ".join(items[:-1]) + ", and " + items[-1]
    print(f"You are bringing {bringing}.")


if __name__ == "__main__":
    main()
