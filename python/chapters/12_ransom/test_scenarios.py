"""Real-world cases for ransom.py: a seed is a promise.

Tests, bug reports and demos rely on "--seed 1 gives this exact note". That only holds if
the program makes the same random calls in the same order, on every Python that runs it.
"""

from subprocess import getstatusoutput

prg = "./ransom.py"


def note(args: str) -> str:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv == 0
    return out


def test_same_seed_same_note():
    """running twice with one seed gives one note"""
    assert note('-s 42 "Pay up by Friday"') == note('-s 42 "Pay up by Friday"')


def test_seed_is_per_character():
    """adding text at the end doesn't change the note before it"""
    short = note('-s 7 "send cash"')
    longer = note('-s 7 "send cash now"')
    assert longer.startswith(short)


def test_only_case_changes():
    """same letters, same order, same punctuation and digits"""
    text = "Give us 2 million dollars, or the cat gets it!"
    out = note(f'-s 3 "{text}"')
    assert out.lower() == text.lower()
    assert [c for c in out if not c.isalpha()] == [c for c in text if not c.isalpha()]


def test_german_sharp_s_keeps_length():
    """'ß'.upper() is 'SS': the note must not grow a letter"""
    for seed in range(1, 20):
        out = note(f'-s {seed} "Straße"')
        assert len(out) == len("Straße")
        assert out.lower() == "straße"


def test_dotted_capital_i_keeps_length():
    """'İ'.lower() is two characters: the note must not grow one"""
    for seed in range(1, 20):
        assert len(note(f'-s {seed} "İstanbul"')) == len("İstanbul")


def test_different_seeds_differ():
    """five seeds don't all give the same note"""
    notes = {note(f'-s {s} "the quick brown fox jumps over the lazy dog"') for s in range(5)}
    assert len(notes) > 1


def test_actually_mixes_case():
    """a long lower-case text comes back with upper-case letters in it"""
    out = note('-s 11 "' + "abcdefghij" * 5 + '"')
    assert any(c.isupper() for c in out) and any(c.islower() for c in out)
