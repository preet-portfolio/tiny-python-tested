#!/usr/bin/env python3
"""Rhymer: swap a word's leading consonant sound for every other one."""

import argparse


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("word", help="A word to rhyme")
    return parser.parse_args()


def stemmer(word):
    """Split a word into (leading consonants, the rest)."""
    return word, ""


def main():
    """Print the rhymes, or say the word can't be rhymed."""
    word = get_args().word
    print(word)


if __name__ == "__main__":
    main()
