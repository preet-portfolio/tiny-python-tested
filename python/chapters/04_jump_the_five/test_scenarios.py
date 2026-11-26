"""Real-world cases for jump.py: masking phone numbers before they reach a log.

A mask that misses some digits leaks the number. Phone numbers arrive typed on phones set to
Arabic, Hindi or Japanese keyboards, and those digits are not '0'-'9'. Every case here must
pass without breaking a single test in the author's test.py.
"""

from subprocess import getstatusoutput

prg = "./jump.py"


def jump(text: str) -> str:
    rv, out = getstatusoutput(f"{prg} '{text}'")
    assert rv == 0, out
    return out


def test_jumping_twice_gives_it_back():
    """the code is its own key: jump, jump again, and the number is back"""
    for text in ["867-5309", "Call 1-800-329-8044 today!", "0"]:
        assert jump(jump(text)) == text


def test_fullwidth_digits():
    """digits typed on a Japanese keyboard are masked too, and stay full-width"""
    assert jump("電話 ０９０-１２３４") == "電話 ５１５-９８７６"


def test_arabic_indic_digits():
    """Arabic phone digits (٠١٢٣٤٥٦٧٨٩) are masked too"""
    assert jump("رقم ٠١٢٣٤٥٦٧٨٩") == "رقم ٥٩٨٧٦٠٤٣٢١"


def test_devanagari_digits():
    """Hindi digits (०१२...) are masked too"""
    assert jump("फ़ोन ९८७६५") == "फ़ोन १२३४०"


def test_no_digit_survives():
    """after masking, no original digit is left in its place"""
    text = "ph: 0123456789 / ٠١٢٣٤٥٦٧٨٩ / ０１２３４５６７８９"
    for a, b in zip(text, jump(text)):
        assert not a.isdecimal() or a != b


def test_only_digits_change():
    """letters, emoji and number-ish symbols like ½ and ² are left alone"""
    assert jump("Room 4½, x² 🎉") == "Room 6½, x² 🎉"
