#!/usr/bin/env python3
"""Heap abuse: Shakespearean insults."""

import argparse
import random

ADJECTIVES = """
bankrupt base caterwauling corrupt cullionly detestable dishonest false filthsome filthy
foolish foul gross heedless indistinguishable infected insatiate irksome lascivious
lecherous loathsome lubbery old peevish rascaly rotten ruinous scurilous scurvy slanderous
sodden-witted thin-faced toad-spotted unmannered vile wall-eyed
""".split()

NOUNS = """
Judas Satan ape ass barbermonger beggar block boy braggart butt carbuncle coward
coxcomb cur dandy degenerate fiend fishmonger fool gull harpy jack jolthead knave liar
lunatic maw milksop minion ratcatcher recreant rogue scold slave swine traitor varlet
villain worm
""".split()


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Heap abuse")
    parser.add_argument("-a", "--adjectives", type=int, default=2, help="Number of adjectives")
    parser.add_argument("-n", "--number", type=int, default=3, help="Number of insults")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    return parser.parse_args()


def main():
    """Print the insults."""
    args = get_args()
    random.seed(args.seed)
    # Your turn: "You <adjective>, <adjective> <noun>!" -- args.number times.
    print("You knave!")


if __name__ == "__main__":
    main()
