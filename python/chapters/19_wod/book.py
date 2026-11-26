#!/usr/bin/env python3
"""Workout of the Day, the book's way: DictReader, random.sample, randint."""

import argparse
import csv
import random
import re
from typing import TextIO


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Create Workout Of (the) Day (WOD)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-f", "--file", metavar="FILE", default="inputs/exercises.csv",
                        type=argparse.FileType("rt"), help="CSV input file of exercises")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("-n", "--num", metavar="exercises", type=int, default=4,
                        help="Number of exercises")
    parser.add_argument("-e", "--easy", action="store_true", help="Halve the reps")
    args = parser.parse_args()
    if args.num < 1:
        parser.error(f'--num "{args.num}" must be greater than 0')
    return args


def read_csv(fh: TextIO) -> list[tuple[str, int, int]]:
    """(name, low, high) for each row whose reps look like 'low-high'."""
    exercises = []
    for row in csv.DictReader(fh, delimiter=","):
        name, reps = row.get("exercise"), row.get("reps")
        if name and reps:
            match = re.match(r"(\d+)-(\d+)$", reps)
            if match:
                exercises.append((name, int(match.group(1)), int(match.group(2))))
    return exercises


def main() -> None:
    """Print today's workout as a table."""
    args = get_args()
    random.seed(args.seed)
    exercises = read_csv(args.file)
    if not exercises:
        raise SystemExit(f'No usable data in --file "{args.file.name}"')
    rows = []
    for name, low, high in random.sample(exercises, k=args.num):
        reps = random.randint(low, high)
        rows.append((name, int(reps / 2) if args.easy else reps))
    width = max([10, *(len(name) for name, _ in rows)])
    print(f"{'Exercise':<{width}}    Reps")
    print(f"{'-' * width}  ------")
    for name, reps in rows:
        print(f"{name:<{width}}  {reps:>6}")


if __name__ == "__main__":
    main()
