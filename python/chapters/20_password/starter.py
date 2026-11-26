#!/usr/bin/env python3
"""Password maker: glue random words into memorable passphrases."""

import argparse
import random


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Password maker")
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"), nargs="+",
                        help="Input file(s)")
    parser.add_argument("-n", "--num", type=int, default=3, help="Number of passwords")
    parser.add_argument("-w", "--num_words", type=int, default=4, help="Words per password")
    parser.add_argument("-m", "--min_word_len", type=int, default=3, help="Minimum word length")
    parser.add_argument("-x", "--max_word_len", type=int, default=6, help="Maximum word length")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    parser.add_argument("-l", "--l33t", action="store_true", help="Obfuscate letters")
    return parser.parse_args()


def clean(word):
    """Only the letters of a word."""
    return word


def ransom(text):
    """Randomly capitalize each letter."""
    return text


def l33t(text):
    """Ransom the text, swap some letters for look-alikes, add a punctuation mark."""
    return text


def main():
    """Print the passwords, one per line."""
    args = get_args()
    random.seed(args.seed)
    print("Your turn!")


if __name__ == "__main__":
    main()
