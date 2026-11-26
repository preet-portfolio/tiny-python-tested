"""Properties of choose() and ransom(), on text Hypothesis generates."""

import importlib.util
import os
import random

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("ransom", os.path.abspath("ransom.py"))
ransom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ransom)

SETTINGS = settings(max_examples=80, derandomize=True, deadline=None, database=None)


@SETTINGS
@given(st.text(max_size=60), st.integers(min_value=0, max_value=2**32))
def test_length_never_changes(text, seed):
    """any text, any seed: the note is as long as the text"""
    random.seed(seed)
    assert len(ransom.ransom(text)) == len(text)


@SETTINGS
@given(st.text(max_size=60), st.integers(min_value=0, max_value=2**32))
def test_one_coin_flip_per_character(text, seed):
    """the generator moves exactly once per character"""
    random.seed(seed)
    ransom.ransom(text)
    after = random.random()
    random.seed(seed)
    for _ in text:
        random.choice([False, True])
    assert random.random() == after


@SETTINGS
@given(st.text(alphabet=st.characters(categories=["Lu", "Ll"]), max_size=40), st.integers(0, 999))
def test_each_letter_is_one_of_its_cases(text, seed):
    """every output letter is the input letter, its upper or its lower case"""
    random.seed(seed)
    for a, b in zip(text, ransom.ransom(text)):
        assert b in {a, a.upper(), a.lower()}
