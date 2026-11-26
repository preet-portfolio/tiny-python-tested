"""Properties of clean(), ransom(), l33t() and passwords(), on input Hypothesis generates."""

import importlib.util
import os
import random
import re
import string

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("password", os.path.abspath("password.py"))
password = importlib.util.module_from_spec(spec)
spec.loader.exec_module(password)

SETTINGS = settings(max_examples=80, derandomize=True, deadline=None, database=None)
letters = st.text(alphabet=string.ascii_letters, max_size=30)
word_lists = st.lists(st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=6),
                      min_size=4, max_size=30, unique=True).map(lambda ws: [w.title() for w in ws])


@SETTINGS
@given(st.text(max_size=30))
def test_clean_keeps_only_letters(word):
    """clean() keeps exactly the A-Z letters, in order"""
    assert password.clean(word) == "".join(c for c in word if c in string.ascii_letters)


@SETTINGS
@given(letters, st.integers(0, 2**32))
def test_ransom_only_changes_case(text, seed):
    """ransom() keeps every letter, only BIG or small changes"""
    random.seed(seed)
    out = password.ransom(text)
    assert out.lower() == text.lower()


@SETTINGS
@given(letters, st.integers(0, 2**32))
def test_l33t_adds_one_mark(text, seed):
    """l33t() is one character longer, and that last one is punctuation"""
    random.seed(seed)
    out = password.l33t(text)
    assert len(out) == len(text) + 1
    assert out[-1] in string.punctuation


@SETTINGS
@given(word_lists, st.integers(1, 4), st.integers(0, 2**32))
def test_passwords_use_different_words_from_the_list(words, num_words, seed):
    """each password is num_words different words from the list, glued together"""
    random.seed(seed)
    for made in password.passwords(words, 3, num_words):
        parts = re.findall("[A-Z][a-z]*", made)
        assert len(parts) == num_words
        assert len(set(parts)) == num_words
        assert set(parts) <= set(words)


@SETTINGS
@given(word_lists, st.integers(0, 2**32))
def test_same_seed_same_passwords(words, seed):
    """the same lucky number makes the same passwords"""
    random.seed(seed)
    first = password.passwords(words, 3, 2)
    random.seed(seed)
    assert password.passwords(words, 3, 2) == first
