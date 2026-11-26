"""Properties of scramble() and scramble_line(), on text Hypothesis generates."""

import importlib.util
import os
import random

from hypothesis import given, settings
from hypothesis import strategies as st

spec = importlib.util.spec_from_file_location("scrambler", os.path.abspath("scrambler.py"))
scrambler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scrambler)

SETTINGS = settings(max_examples=80, derandomize=True, deadline=None, database=None)
words = st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1,
                max_size=14)
lines = st.text(alphabet=st.sampled_from(list("abcdeXYZ'., -!0123")), max_size=60)


@SETTINGS
@given(words, st.integers(0, 2**32))
def test_same_letters_first_and_last_kept(word, seed):
    """a scrambled word has the same letters, and the same first and last letter"""
    random.seed(seed)
    out = scrambler.scramble(word)
    assert sorted(out) == sorted(word)
    assert out[0] == word[0] and out[-1] == word[-1]


@SETTINGS
@given(st.text(alphabet="abcXYZ", max_size=3), st.integers(0, 999))
def test_short_words_untouched(word, seed):
    """words of three letters or fewer can't be scrambled, so they aren't"""
    random.seed(seed)
    assert scrambler.scramble(word) == word


@SETTINGS
@given(lines, st.integers(0, 2**32))
def test_only_letters_move(line, seed):
    """the line is as long as before; spaces, digits and punctuation stay in place

    (an apostrophe counts as part of a word, so "Don't" may become "Do'nt")"""
    random.seed(seed)
    out = scrambler.scramble_line(line)
    assert len(out) == len(line)
    assert [(i, c) for i, c in enumerate(out) if not c.isalpha() and c != "'"] == \
        [(i, c) for i, c in enumerate(line) if not c.isalpha() and c != "'"]


@SETTINGS
@given(lines, st.integers(0, 2**32))
def test_seed_means_same_line(line, seed):
    """same seed, same scramble"""
    random.seed(seed)
    first = scrambler.scramble_line(line)
    random.seed(seed)
    assert scrambler.scramble_line(line) == first
