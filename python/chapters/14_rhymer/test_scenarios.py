"""Real-world cases for rhymer.py: brand-name variants from a stem.

Marketing teams feed a product name in and want a list of sound-alikes to check. The book's
rule splits on the first a, e, i, o or u, which goes odd on qu-words, accented letters and
a name pasted with a space in front.
"""

from subprocess import getoutput

prg = "./rhymer.py"


def rhymes(word: str) -> list[str]:
    return getoutput(f"{prg} {word!r}").splitlines()


def test_q_brings_its_u():
    """'take' rhymes with 'quake', never 'qake'"""
    out = rhymes("take")
    assert "quake" in out
    assert "qake" not in out
    assert len(out) == 56


def test_qu_is_one_sound():
    """'queen' swaps 'qu' as a whole: green, screen, spleen, never 'bueen'"""
    out = rhymes("queen")
    for word in ("green", "screen", "spleen", "teen"):
        assert word in out
    assert not any(w.endswith("ueen") and not w.endswith("queen") for w in out)
    assert "queen" not in out


def test_accented_vowels_are_vowels():
    """'éclair' starts with a vowel, so it rhymes: béclair, cléclair"""
    out = rhymes("éclair")
    assert len(out) == 57
    assert "béclair" in out and "cléclair" in out


def test_accent_after_a_consonant():
    """'café' splits after the c: bafé, chafé"""
    out = rhymes("café")
    assert "bafé" in out and "chafé" in out


def test_spaces_around_are_ignored():
    """a name pasted with spaces around it still rhymes"""
    assert rhymes("  cake ") == rhymes("cake")


def test_never_rhymes_with_itself_or_repeats():
    """no word appears twice, and the word itself isn't on its own list"""
    for word in ("take", "chair", "apple", "queen", "squid", "string"):
        out = rhymes(word)
        assert len(out) == len(set(out))
        assert word not in out
