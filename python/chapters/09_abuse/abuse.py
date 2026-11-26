#!/usr/bin/env python3
"""Heap abuse: Shakespearean insults, reproducible with --seed."""

import argparse
import math
import random

_ADJECTIVES = """
bankrupt base caterwauling corrupt cullionly detestable dishonest false filthsome filthy
foolish foul gross heedless indistinguishable infected insatiate irksome lascivious
lecherous loathsome lubbery old peevish rascaly rotten ruinous scurilous scurvy slanderous
sodden-witted thin-faced toad-spotted unmannered vile wall-eyed
"""
ADJECTIVES = _ADJECTIVES.split()

_NOUNS = """
Judas Satan ape ass barbermonger beggar block boy braggart butt carbuncle coward coxcomb cur
dandy degenerate fiend fishmonger fool gull harpy jack jolthead knave liar lunatic maw
milksop minion ratcatcher recreant rogue scold slave swine traitor varlet villain worm
"""
NOUNS = _NOUNS.split()


def get_args() -> argparse.Namespace:
    """Parse and check the command line."""
    parser = argparse.ArgumentParser(
        description="Heap abuse",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-a", "--adjectives", metavar="adjectives", type=int, default=2,
                        help="Number of adjectives")
    parser.add_argument("-n", "--number", metavar="insults", type=int, default=3,
                        help="Number of insults")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    args = parser.parse_args()
    if args.adjectives < 1:
        parser.error(f'--adjectives "{args.adjectives}" must be > 0')
    if args.adjectives > len(ADJECTIVES):
        parser.error(f'--adjectives "{args.adjectives}" must be <= {len(ADJECTIVES)}')
    if args.number < 1:
        parser.error(f'--number "{args.number}" must be > 0')
    if args.number > possible(args.adjectives):
        parser.error(f'--number "{args.number}" must be <= {possible(args.adjectives)}, '
                     "the number of different insults")
    return args


def possible(adjectives: int) -> int:
    """How many different insults there are with this many adjectives."""
    return math.perm(len(ADJECTIVES), adjectives) * len(NOUNS)


def insult(adjectives: int) -> str:
    """One insult: distinct adjectives, then a noun."""
    adjs = ", ".join(random.sample(ADJECTIVES, k=adjectives))
    return f"You {adjs} {random.choice(NOUNS)}!"


def insults(number: int, adjectives: int) -> list[str]:
    """``number`` different insults. A repeat is thrown away and drawn again.

    The draws are capped (repeats are rare, so the cap is never reached for a number
    get_args() allows) so that a bug here can't loop forever.
    """
    out: list[str] = []
    seen: set[str] = set()
    for _ in range(number * 20 + 100):
        if len(out) == number:
            break
        line = insult(adjectives)
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def main() -> None:
    """Print the insults."""
    args = get_args()
    random.seed(args.seed)
    print("\n".join(insults(args.number, args.adjectives)))


if __name__ == "__main__":
    main()
