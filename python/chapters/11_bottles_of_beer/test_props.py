"""Properties every verse must have, checked on numbers Hypothesis picks.

The two example verses in test_unit.py can pass by accident. These can't, for any n.
"""

import importlib.util
import os
import re

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("bottles", os.path.abspath("bottles.py"))
bottles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bottles)


@settings(max_examples=60, derandomize=True, deadline=None, database=None)
@given(st.integers(min_value=2, max_value=10_000))
def test_counts_down_by_one(n):
    """the verse starts at n and ends at n - 1"""
    lines = bottles.verse(n, "beer").splitlines()
    assert lines[0].startswith(f"{n} bottles ")
    assert lines[-1].startswith(f"{n - 1} bottle")


@settings(max_examples=60, derandomize=True, deadline=None, database=None)
@given(st.integers(min_value=1, max_value=10_000))
def test_never_says_1_bottles_or_0_bottles(n):
    """'1 bottles' and '0 bottles' never appear"""
    text = bottles.verse(n, "beer")
    assert not re.search(r"(?<!\d)1 bottles", text)
    assert not re.search(r"(?<!\d)0 bottle", text)
    assert len(text.splitlines()) == 4
