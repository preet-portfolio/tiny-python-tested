#!/usr/bin/env python3
"""Password maker: glue random words from a word list into memorable passphrases."""

import argparse
import random
import re
import string
from collections.abc import Iterable

LEET = str.maketrans({"a": "@", "A": "4", "O": "0", "t": "+", "E": "3", "I": "1", "S": "5"})


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Password maker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"), nargs="+",
                        help="Input file(s) ('-' reads STDIN)")
    parser.add_argument("-n", "--num", metavar="num_passwords", type=int, default=3,
                        help="Number of passwords to generate")
    parser.add_argument("-w", "--num_words", metavar="num_words", type=int, default=4,
                        help="Number of words to use for password")
    parser.add_argument("-m", "--min_word_len", metavar="minimum", type=int, default=3,
                        help="Minimum word length")
    parser.add_argument("-x", "--max_word_len", metavar="maximum", type=int, default=6,
                        help="Maximum word length")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("-l", "--l33t", action="store_true", help="Obfuscate letters")
    args = parser.parse_args()
    for flag, value in (("--num", args.num), ("--num_words", args.num_words)):
        if value < 1:
            parser.error(f'{flag} "{value}" must be at least 1')
    if args.min_word_len > args.max_word_len:
        parser.error(f'--min_word_len "{args.min_word_len}" is bigger than '
                     f'--max_word_len "{args.max_word_len}"')
    return args


def clean(word: str) -> str:
    """Only the letters: "Don't" -> 'Dont'."""
    return re.sub("[^a-zA-Z]", "", word)


def ransom(text: str) -> str:
    """One coin flip per letter: upper case on heads, lower case on tails."""
    return "".join(c.upper() if random.choice([False, True]) else c.lower() for c in text)


def l33t(text: str) -> str:
    """Ransom-case the text, swap some letters for look-alikes, add a punctuation mark."""
    return ransom(text).translate(LEET) + random.choice(string.punctuation)


def read_words(lines: Iterable[str], shortest: int, longest: int) -> list[str]:
    """Every different word of the right length, title-cased, in sorted order."""
    words = set()
    for line in lines:
        for word in map(clean, line.lower().split()):
            if shortest <= len(word) <= longest:
                words.add(word.title())
    return sorted(words)


def passwords(words: list[str], num: int, num_words: int) -> list[str]:
    """``num`` passwords, each ``num_words`` different words glued together."""
    return ["".join(random.sample(words, k=num_words)) for _ in range(num)]


def main() -> None:
    """Print the passwords, one per line."""
    args = get_args()
    random.seed(args.seed)
    words = read_words((line for fh in args.file for line in fh),
                       args.min_word_len, args.max_word_len)
    if len(words) < args.num_words:
        raise SystemExit(f"Found {len(words)} different words of {args.min_word_len} to "
                         f"{args.max_word_len} letters, but each password needs "
                         f"{args.num_words}.")
    made = passwords(words, args.num, args.num_words)
    print("\n".join(map(l33t, made) if args.l33t else made))


if __name__ == "__main__":
    main()
