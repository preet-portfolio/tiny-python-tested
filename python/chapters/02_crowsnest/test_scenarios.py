"""Real-world cases for crowsnest.py that the book's tests don't cover.

The book's rule is "a vowel letter takes 'an'". English picks the article by the *sound*,
which is where generated copy ("You unlocked a/an ___ badge") goes wrong in production.
Every case here must pass without breaking a single test in the author's test.py.
"""

from subprocess import getoutput

prg = "./crowsnest.py"
template = "Ahoy, Captain, {} {} off the larboard bow!"


def check(word: str, article: str) -> None:
    out = getoutput(f"{prg} {word}")
    assert out.strip() == template.format(article, word)


def test_silent_h():
    """hour, honest and heir start with a vowel sound"""
    for word in ["hour", "hourglass", "honest", "honorable", "heir", "Hour"]:
        check(word, "an")


def test_you_sound():
    """unicorn, university and European start with a 'y' sound"""
    for word in ["unicorn", "university", "European", "user", "usual", "utility", "ewe"]:
        check(word, "a")


def test_w_sound():
    """one and once start with a 'w' sound"""
    for word in ["one", "once"]:
        check(word, "a")


def test_initialisms():
    """letters read one by one: an FBI agent, an MRI, a UFO"""
    for word, article in [("FBI", "an"), ("MRI", "an"), ("UFO", "a"), ("X", "an")]:
        check(word, article)


def test_hyphen_and_digits():
    """the first thing said aloud decides: an 8-ball, a 1-eyed whale"""
    for word, article in [("8-ball", "an"), ("11th-hour", "an"), ("18-wheeler", "an"), ("1-eyed", "a"),
                          ("180-day", "a"), ("2", "a")]:
        check(word, article)


def test_still_a_plain_vowel():
    """the book's cases keep working: an octopus, a narwhal, an upbound"""
    for word, article in [("octopus", "an"), ("narwhal", "a"), ("upbound", "an")]:
        check(word, article)
