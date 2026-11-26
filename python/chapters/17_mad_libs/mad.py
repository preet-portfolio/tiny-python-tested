#!/usr/bin/env python3
"""Mad Libs: fill the <placeholders> in a story with your own words."""

import argparse
import re
import sys

# A blank is <words> with no space just inside the brackets, so "5 < 6 and 7 > 3" is maths,
# not a blank.
BLANK = re.compile(r"<([^<>\s](?:[^<>]*[^<>\s])?)>")


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Mad Libs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file", metavar="FILE", type=argparse.FileType("rt"),
                        help="Input file ('-' reads the story from STDIN)")
    parser.add_argument("-i", "--inputs", metavar="input", nargs="*", default=None,
                        help="Inputs (for testing)")
    return parser.parse_args()


def article(word: str) -> str:
    """'an' before a vowel letter, 'a' otherwise."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def blanks(text: str) -> list[str]:
    """The name of every blank, in order: ['adjective', 'noun', ...]."""
    return BLANK.findall(text)


def fill(text: str, answers: list[str]) -> str:
    """Put each answer into the next blank, exactly as typed (backslashes included)."""
    words = iter(answers)
    return BLANK.sub(lambda _: next(words), text)


def ask(names: list[str]) -> list[str]:
    """Ask for each blank at the keyboard."""
    answers = []
    for name in names:
        try:
            answers.append(input(f"Give me {article(name)} {name}: "))
        except EOFError:
            # On STDOUT, right after the prompts it answers.
            print(f"\nStopped: still needed {article(name)} {name}.")
            sys.exit(1)
    return answers


def main() -> None:
    """Find the blanks, get the answers, print the story."""
    args = get_args()
    with args.file as fh:
        text = fh.read().rstrip()
    names = blanks(text)
    if not names:
        sys.exit(f'"{args.file.name}" has no placeholders.')
    if args.inputs is None:
        answers = ask(names)
    else:
        answers = args.inputs
        if len(answers) != len(names):
            need = ", ".join(names)
            sys.exit(f"The story has {len(names)} blanks ({need}) "
                     f"but got {len(answers)} answers.")
    print(fill(text, answers))


if __name__ == "__main__":
    main()
