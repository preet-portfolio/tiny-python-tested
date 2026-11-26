#!/usr/bin/env python3
"""Picnic: say what you're bringing."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Picnic game")
    parser.add_argument("item", metavar="str", nargs="+", help="Item(s) to bring")
    parser.add_argument("-s", "--sorted", action="store_true", help="Sort the items")
    return parser.parse_args()


def main():
    """Print what we're bringing."""
    args = get_args()
    # Your turn: one item, two items and three or more each read differently.
    print(args.item)


if __name__ == "__main__":
    main()
