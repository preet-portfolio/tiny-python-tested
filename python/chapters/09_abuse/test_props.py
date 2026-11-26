"""Properties of insults(), for numbers Hypothesis picks."""

import importlib.util
import os
import random

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("abuse", os.path.abspath("abuse.py"))
abuse = importlib.util.module_from_spec(spec)
spec.loader.exec_module(abuse)

SETTINGS = settings(max_examples=60, derandomize=True, deadline=None, database=None)
seeds = st.integers(min_value=0, max_value=2**32)


@SETTINGS
@given(seeds, st.integers(1, 40), st.integers(1, 6))
def test_every_insult_is_well_formed(seed, number, adjectives):
    """n lines, each 'You adj, adj noun!' with words from the lists and no repeated adjective"""
    random.seed(seed)
    lines = abuse.insults(number, adjectives)
    assert len(lines) == number
    for line in lines:
        assert line.startswith("You ") and line.endswith("!")
        *adjs, noun = line[4:-1].replace(",", "").split(" ")
        assert noun in abuse.NOUNS
        assert len(adjs) == adjectives == len(set(adjs))
        assert set(adjs) <= set(abuse.ADJECTIVES)


@SETTINGS
@given(seeds, st.integers(1, 60))
def test_never_repeats(seed, number):
    """no two insults in one batch are the same, even with one adjective"""
    random.seed(seed)
    lines = abuse.insults(number, 1)
    assert len(set(lines)) == len(lines)


@SETTINGS
@given(seeds, st.integers(1, 20), st.integers(1, 20), st.integers(1, 4))
def test_longer_batch_starts_the_same(seed, a, b, adjectives):
    """a bigger batch begins with the smaller batch"""
    small, big = sorted((a, b))
    random.seed(seed)
    first = abuse.insults(small, adjectives)
    random.seed(seed)
    assert abuse.insults(big, adjectives)[:small] == first
