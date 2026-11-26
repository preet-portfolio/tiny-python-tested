"""Unit tests: call verse() directly instead of running the program."""

import importlib.util
import os

import pytest


@pytest.fixture(scope="module")
def bottles():
    spec = importlib.util.spec_from_file_location("bottles", os.path.abspath("bottles.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verse_last(bottles):
    """the last verse is singular and ends with 'No more'"""
    assert bottles.verse(1).splitlines() == [
        "1 bottle of beer on the wall,",
        "1 bottle of beer,",
        "Take one down, pass it around,",
        "No more bottles of beer on the wall!",
    ]


def test_verse_two(bottles):
    """two bottles goes down to one bottle, singular"""
    assert bottles.verse(2).splitlines() == [
        "2 bottles of beer on the wall,",
        "2 bottles of beer,",
        "Take one down, pass it around,",
        "1 bottle of beer on the wall!",
    ]
