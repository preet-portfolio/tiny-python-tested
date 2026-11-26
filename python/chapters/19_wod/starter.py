#!/usr/bin/env python3
"""Workout of the Day: pick random exercises and reps from a CSV file."""

import argparse
import random


def get_args():
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Create Workout Of (the) Day (WOD)")
    parser.add_argument("-f", "--file", default="inputs/exercises.csv",
                        type=argparse.FileType("rt"), help="CSV input file of exercises")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed")
    parser.add_argument("-n", "--num", type=int, default=4, help="Number of exercises")
    parser.add_argument("-e", "--easy", action="store_true", help="Halve the reps")
    return parser.parse_args()


def read_csv(fh):
    """A list of (name, low, high) for each good row of the file."""
    return []


def main():
    """Print today's workout."""
    args = get_args()
    random.seed(args.seed)
    print(read_csv(args.file))


if __name__ == "__main__":
    main()
