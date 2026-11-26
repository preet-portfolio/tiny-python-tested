#!/usr/bin/env python3
"""Password maker, the book's way: a set of title-cased words and random.sample."""

import argparse
import random
import re
import string

LEET = str.maketrans({"a": "@", "A": "4", "O": "0", "t": "+", "E": "3", "I": "1", "S": "5"})


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Password maker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"), nargs="+",
                        help="Input file(s)")
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
    return parser.parse_args()


def clean(word: str) -> str:
    """Only the letters."""
    return re.sub("[^a-zA-Z]", "", word)


def ransom(text: str) -> str:
    """Randomly capitalize each letter."""
    return "".join(c.upper() if random.choice([False, True]) else c.lower() for c in text)


def l33t(text: str) -> str:
    """Ransom, substitute, add punctuation."""
    return ransom(text).translate(LEET) + random.choice(string.punctuation)


def passwords(words: list[str], num: int, num_words: int) -> list[str]:
    """``num`` passwords of ``num_words`` words."""
    return ["".join(random.sample(words, k=num_words)) for _ in range(num)]


def main() -> None:
    """Print the passwords."""
    args = get_args()
    random.seed(args.seed)
    words = set()
    for fh in args.file:
        for line in fh:
            for word in map(clean, line.lower().split()):
                if args.min_word_len <= len(word) <= args.max_word_len:
                    words.add(word.title())
    made = passwords(sorted(words), args.num, args.num_words)
    print("\n".join(map(l33t, made) if args.l33t else made))


if __name__ == "__main__":
    main()
