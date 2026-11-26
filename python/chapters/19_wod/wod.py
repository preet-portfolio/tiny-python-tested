#!/usr/bin/env python3
"""Workout of the Day: pick random exercises and reps from a CSV file."""

import argparse
import csv
import random
import re
from typing import TextIO

Exercise = tuple[str, int, int]


def get_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description="Create Workout Of (the) Day (WOD)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-f", "--file", metavar="FILE", default="inputs/exercises.csv",
                        type=argparse.FileType("rt", encoding="utf-8-sig"),
                        help="CSV input file of exercises ('-' reads STDIN)")
    parser.add_argument("-s", "--seed", metavar="seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("-n", "--num", metavar="exercises", type=int, default=4,
                        help="Number of exercises")
    parser.add_argument("-e", "--easy", action="store_true", help="Halve the reps")
    args = parser.parse_args()
    if args.num < 1:
        parser.error(f'--num "{args.num}" must be greater than 0')
    return args


def read_csv(fh: TextIO) -> list[Exercise]:
    """Rows with an 'exercise' name and 'low-high' reps; anything else is skipped.

    Spreadsheet quirks are forgiven: a byte-order mark before the header, spaces around a
    value, a range written backwards (50-20), and the same exercise listed twice.
    """
    exercises: dict[str, Exercise] = {}
    reader = csv.DictReader(fh, delimiter=",")
    reader.fieldnames = [name.lstrip("﻿") for name in reader.fieldnames or []]
    for row in reader:
        name = (row.get("exercise") or "").strip()
        match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", row.get("reps") or "")
        if name and match and name.lower() not in exercises:
            low, high = sorted((int(match.group(1)), int(match.group(2))))
            exercises[name.lower()] = (name, low, high)
    return list(exercises.values())


def format_table(rows: list[tuple[str, int]]) -> str:
    """A plain text table: names on the left, reps lined up on the right."""
    headers = ("Exercise", "Reps")
    left = max([len(headers[0]) + 2, *(len(name) for name, _ in rows)])
    right = max([len(headers[1]) + 2, *(len(str(reps)) for _, reps in rows)])
    lines = [f"{headers[0]:<{left}}  {headers[1]:>{right}}", f"{'-' * left}  {'-' * right}"]
    lines += [f"{name:<{left}}  {reps:>{right}}" for name, reps in rows]
    return "\n".join(lines)


def workout(exercises: list[Exercise], num: int, easy: bool) -> list[tuple[str, int]]:
    """Pick ``num`` different exercises and a number of reps for each."""
    rows = []
    for name, low, high in random.sample(exercises, k=num):
        reps = random.randint(low, high)
        rows.append((name, max(1, reps // 2) if easy else reps))
    return rows


def main() -> None:
    """Print today's workout."""
    args = get_args()
    random.seed(args.seed)
    with args.file as fh:
        exercises = read_csv(fh)
    if not exercises:
        raise SystemExit(f'No usable data in --file "{args.file.name}"')
    if args.num > len(exercises):
        raise SystemExit(f'--num "{args.num}" is more than the {len(exercises)} '
                         f'exercises in "{args.file.name}"')
    print(format_table(workout(exercises, args.num, args.easy)))


if __name__ == "__main__":
    main()
