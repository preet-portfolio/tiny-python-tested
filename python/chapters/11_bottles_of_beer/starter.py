#!/usr/bin/env python3
"""Bottles of Beer: sing the countdown."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Bottles of beer song")
    parser.add_argument("-n", "--num", type=int, default=10, help="How many bottles")
    return parser.parse_args()


def verse(n):
    """One verse, starting with n bottles on the wall."""
    return ""


def main():
    """Sing every verse from --num down to 1."""
    num = get_args().num
    print(verse(num))


if __name__ == "__main__":
    main()
