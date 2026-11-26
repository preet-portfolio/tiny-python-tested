"""Real-world cases for wod.py: a plan generated from a spreadsheet export.

The book's CSV files are tidy. Real ones come out of Excel or Google Sheets with a hidden
byte-order mark, spaces after commas, ranges typed backwards and rows pasted twice. And
people ask for more than the list has.
"""

import importlib.util
import io
import os
from subprocess import getstatusoutput

prg = "./wod.py"


def csv_file(name: str, text: str) -> str:
    """Write a CSV next to the tests (left there so the command can be rerun by hand)."""
    path = f"wod-{name}.csv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return path


def rows(out: str) -> list[tuple[str, int]]:
    result = []
    for line in out.splitlines()[2:]:
        name, reps = line.rsplit(maxsplit=1)
        result.append((name.strip(), int(reps)))
    return result


def test_too_many_exercises_is_a_clear_error():
    """asking for 20 exercises from a list of 9 says so, no crash"""
    rv, out = getstatusoutput(f"{prg} -n 20 -s 1")
    assert rv != 0
    assert "Traceback" not in out
    assert "9" in out


def test_spreadsheet_byte_order_mark():
    """a CSV saved by Excel starts with an invisible mark, and still works"""
    path = csv_file("bom", "﻿exercise,reps\nHops,10-20\nSkips,5-10\n")
    rv, out = getstatusoutput(f"{prg} -f {path} -n 2 -s 1")
    assert rv == 0
    assert sorted(name for name, _ in rows(out)) == ["Hops", "Skips"]


def test_spaces_after_commas():
    """'Hops, 10 - 20' is read as Hops, 10 to 20 reps"""
    path = csv_file("spaces", "exercise,reps\nHops, 10 - 20\n")
    rv, out = getstatusoutput(f"{prg} -f {path} -n 1 -s 3")
    assert rv == 0
    [(name, reps)] = rows(out)
    assert name == "Hops" and 10 <= reps <= 20


def test_backwards_range():
    """'50-20' means between 20 and 50, it doesn't crash"""
    path = csv_file("backwards", "exercise,reps\nStar jumps,50-20\n")
    for seed in range(1, 6):
        rv, out = getstatusoutput(f"{prg} -f {path} -n 1 -s {seed}")
        assert rv == 0
        [(_, reps)] = rows(out)
        assert 20 <= reps <= 50


def test_easy_never_means_zero():
    """halving 1 rep gives 1 rep, not 0"""
    path = csv_file("tiny", "exercise,reps\nCartwheels,1-1\n")
    rv, out = getstatusoutput(f"{prg} -f {path} -n 1 -e -s 1")
    assert rv == 0
    assert rows(out) == [("Cartwheels", 1)]


def test_no_exercise_twice():
    """a row pasted twice can't put the same exercise in the plan twice"""
    path = csv_file("twice", "exercise,reps\nHops,10-20\nHops,10-20\nSkips,5-10\n")
    for seed in range(1, 10):
        rv, out = getstatusoutput(f"{prg} -f {path} -n 2 -s {seed}")
        assert rv == 0
        names = [name for name, _ in rows(out)]
        assert sorted(names) == ["Hops", "Skips"]


def test_empty_file_is_a_clear_error():
    """a file with no exercises in it says so"""
    rv, out = getstatusoutput(f"{prg} -f inputs/bad-empty.csv")
    assert rv != 0
    assert "No usable data" in out


def test_table_lines_up_for_long_names():
    """the reps column lines up even with a very long exercise name"""
    path = csv_file("long", "exercise,reps\nSuper extra long wiggly dance,10-20\nHop,5-9\n")
    rv, out = getstatusoutput(f"{prg} -f {path} -n 2 -s 2")
    assert rv == 0
    lines = out.splitlines()
    assert len({len(line) for line in lines}) == 1


def test_read_csv_forgives_a_messy_stream():
    """read_csv itself skips the hidden mark and treats 'Hops' and 'hops ' as one exercise"""
    spec = importlib.util.spec_from_file_location("wod_module", os.path.abspath("wod.py"))
    wod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wod)
    text = "\ufeffexercise,reps\nHops ,10-20\nhops,1-2\nSkips,5-10\n"
    assert wod.read_csv(io.StringIO(text)) == [("Hops", 10, 20), ("Skips", 5, 10)]
