"""Properties of mutate(), on text Hypothesis generates."""

import importlib.util
import os
import random

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("telephone", os.path.abspath("telephone.py"))
telephone = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telephone)

SETTINGS = settings(max_examples=80, derandomize=True, deadline=None, database=None)
seeds = st.integers(min_value=0, max_value=2**32)
rates = st.floats(min_value=0, max_value=1)


@SETTINGS
@given(st.text(max_size=60), seeds, rates)
def test_same_length(text, seed, rate):
    """the message never grows or shrinks"""
    random.seed(seed)
    assert len(telephone.mutate(text, rate)) == len(text)


@SETTINGS
@given(st.text(alphabet=st.characters(exclude_characters="\n"), min_size=1, max_size=60),
       seeds, st.floats(min_value=0.01, max_value=1))
def test_some_change_whenever_asked(text, seed, rate):
    """any rate above zero changes at least one character"""
    random.seed(seed)
    out = telephone.mutate(text, rate)
    assert sum(a != b for a, b in zip(text, out)) >= 1


@SETTINGS
@given(st.text(alphabet="ab \n", max_size=40), seeds, rates)
def test_newlines_never_move(text, seed, rate):
    """line breaks are exactly where they were"""
    random.seed(seed)
    out = telephone.mutate(text, rate)
    assert [c == "\n" for c in out] == [c == "\n" for c in text]


@SETTINGS
@given(st.text(max_size=60), seeds)
def test_zero_changes_nothing(text, seed):
    """-m 0 is a perfect echo"""
    random.seed(seed)
    assert telephone.mutate(text, 0) == text
