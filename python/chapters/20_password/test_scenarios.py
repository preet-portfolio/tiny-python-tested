"""Real-world cases for password.py: what happens with a small or odd word list.

A passphrase is only as good as the list it's drawn from. With a short list, or settings
that filter every word out, the program must say so clearly instead of crashing, and it
must never quietly hand out a password with fewer words than asked for.
"""

from subprocess import getstatusoutput

prg = "./password.py"


def word_file(name: str, text: str) -> str:
    """Write a word list next to the tests (left there so the command can be rerun)."""
    path = f"words-{name}.txt"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def test_too_few_words_is_a_clear_error():
    """three words and four per password: say so, no crash"""
    path = word_file("three", "apple banana cherry\n")
    rv, out = getstatusoutput(f"{prg} {path} -s 1")
    assert rv != 0
    assert "Traceback" not in out
    assert "3 different words" in out


def test_every_word_filtered_out():
    """if no word is the right length, say so"""
    path = word_file("short", "a an ox it\n")
    rv, out = getstatusoutput(f"{prg} {path} -s 1")
    assert rv != 0
    assert "Traceback" not in out
    assert "0 different words" in out


def test_min_bigger_than_max():
    """shortest 8 letters, longest 4 letters can't both be true"""
    rv, out = getstatusoutput(f"{prg} ../inputs/words.txt -m 8 -x 4")
    assert rv != 0
    assert "--min_word_len" in out and "Traceback" not in out


def test_zero_words_is_refused():
    """a password of zero words would be empty: refused"""
    rv, out = getstatusoutput(f"{prg} ../inputs/words.txt -w 0")
    assert rv != 0
    assert "--num_words" in out


def test_same_word_counted_once():
    """'Cat cat CAT' is one word, so two-word passwords need another word"""
    path = word_file("cats", "Cat cat CAT\n")
    rv, out = getstatusoutput(f"{prg} {path} -w 2")
    assert rv != 0
    assert "1 different words" in out


def test_no_word_twice_in_a_password():
    """with just two words, every password uses both, once each"""
    path = word_file("two", "moon\nstar\n")
    rv, out = getstatusoutput(f"{prg} {path} -w 2 -n 5 -s 7")
    assert rv == 0
    assert set(out.splitlines()) <= {"MoonStar", "StarMoon"}


def test_several_files_share_one_list():
    """words from two files make one list"""
    a = word_file("a", "moon\n")
    b = word_file("b", "star\n")
    rv, out = getstatusoutput(f"{prg} {a} {b} -w 2 -n 1 -s 1")
    assert rv == 0
    assert out in ("MoonStar", "StarMoon")
