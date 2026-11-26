"""Real-world cases for picnic.py: lists in notifications.

"Ana, Ben, and 2 others are coming" is built from user input: names with stray spaces,
blank form fields, the same name twice, capitals and accents. The book's rules cover tidy
words only. Every case here must pass without breaking a single test in the author's test.py.
"""

from subprocess import getstatusoutput

prg = "./picnic.py"


def bring(args: str) -> str:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv == 0, out
    return out.strip()


def test_sort_ignores_capitals():
    """a capital letter doesn't jump the queue"""
    assert bring("-s apple Banana") == "You are bringing apple and Banana."
    assert bring("-s zucchini Apples bread") == "You are bringing Apples, bread, and zucchini."


def test_sort_ignores_accents():
    """éclairs sort with the e's, not after z"""
    assert bring("-s figs éclairs apples") == "You are bringing apples, éclairs, and figs."


def test_blank_items_are_skipped():
    """an empty form field doesn't become an empty list entry"""
    assert bring('"" chips "   "') == "You are bringing chips."
    assert bring('soda "" cake') == "You are bringing soda and cake."


def test_extra_spaces_are_trimmed():
    """spaces around and inside an item are tidied"""
    assert bring('"  chips " "ice    cream"') == "You are bringing chips and ice cream."


def test_repeats_listed_once():
    """the same thing twice is listed once, first spelling wins"""
    assert bring("chips soda Chips") == "You are bringing chips and soda."


def test_items_with_commas_use_semicolons():
    """'salt, pepper' is one item, so the list switches to semicolons"""
    out = bring('"salt, pepper" chips cake')
    assert out == "You are bringing salt, pepper; chips; and cake."


def test_nothing_to_bring():
    """only blanks is an error, not 'You are bringing .'"""
    rv, out = getstatusoutput(f'{prg} "" " "')
    assert rv != 0
    assert "usage" in out.lower()


def test_tidy_lists_unchanged():
    """the book's own examples still read the same"""
    assert bring("chips") == "You are bringing chips."
    assert bring("-s salad soda cupcakes") == "You are bringing cupcakes, salad, and soda."
