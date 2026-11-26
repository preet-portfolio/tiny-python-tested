"""Real-world cases for abuse.py: reproducible fake test data.

Seeded generators like this one fill test databases with fake names and fake reviews. That
needs three promises: the same seed gives the same rows, asking for more rows doesn't change
the first ones, and no row is a duplicate (a unique column would reject it). Impossible
requests should get a message, not a crash. Every case here must pass without breaking a
single test in the author's test.py.
"""

from subprocess import getstatusoutput

prg = "./abuse.py"


def abuse(args: str) -> list[str]:
    rv, out = getstatusoutput(f"{prg} {args}")
    assert rv == 0, out
    return out.splitlines()


def test_same_seed_same_insults():
    """one seed, run twice, gives the same lines"""
    assert abuse("-s 42 -n 10") == abuse("-s 42 -n 10")


def test_more_insults_keep_the_first_ones():
    """asking for 8 starts with the same 3 you got when asking for 3"""
    assert abuse("-s 9 -n 8")[:3] == abuse("-s 9 -n 3")


def test_no_repeated_insults():
    """300 insults, every one different"""
    lines = abuse("-s 3 -a 1 -n 300")
    assert len(lines) == 300
    assert len(set(lines)) == 300


def test_no_repeated_adjective_in_one_insult():
    """'You vile, vile worm!' never happens"""
    for line in abuse("-s 5 -a 10 -n 20"):
        adjs = line.removeprefix("You ").rsplit(" ", 1)[0].split(", ")
        assert len(adjs) == 10 == len(set(adjs))


def test_too_many_adjectives_is_polite():
    """there are 36 adjectives; asking for 40 gets a message, not a crash"""
    rv, out = getstatusoutput(f"{prg} -s 1 -a 40")
    assert rv != 0
    assert "Traceback" not in out
    assert out.lower().startswith("usage")


def test_too_many_insults_is_polite():
    """with one adjective there are only 1,404 different insults"""
    rv, out = getstatusoutput(f"{prg} -s 1 -a 1 -n 2000")
    assert rv != 0
    assert out.lower().startswith("usage")


def test_different_seeds_differ():
    """five seeds don't all give the same insults"""
    assert len({tuple(abuse(f"-s {s}")) for s in range(5)}) > 1


def test_every_word_at_once():
    """all 36 adjectives in one insult is allowed, and none repeats"""
    (line,) = abuse("-s 1 -a 36 -n 1")
    assert len(set(line.split(", "))) == 36


def test_every_possible_insult():
    """one adjective each: all 1,404 different insults can be asked for"""
    assert len(set(abuse("-s 1 -a 1 -n 1404"))) == 1404
