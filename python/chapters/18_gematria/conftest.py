"""Skip the book's tests that read a text we can't share, when it isn't here.

an English translation of an Issa haiku isn't covered by the book's MIT licence, so it isn't in this repository or on the
site (see python/upstream/unshared.json). CI downloads it and runs these tests; in the
browser, and before `python -m tptl.unshared`, they're skipped rather than failed.
"""

import os

import pytest

TEXT = os.path.join(os.path.dirname(__file__), "../inputs/spiders.txt")
NEEDS_TEXT = {"test_spiders"}
WHY = "Needs an English translation of an Issa haiku, which we can't share. CI runs this rule with the book's file."


def pytest_collection_modifyitems(items: list) -> None:
    if os.path.exists(TEXT):
        return
    for item in items:
        if item.name in NEEDS_TEXT:
            item.add_marker(pytest.mark.skip(reason=WHY))
