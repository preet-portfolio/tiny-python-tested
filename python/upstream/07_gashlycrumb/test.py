#!/usr/bin/env python3
"""tests for gashlycrumb.py"""

# Changed from the book (kyclark/tiny_python_projects @ bcf4b24): test_a, test_b_c and
# test_y quoted lines of Edward Gorey's The Gashlycrumb Tinies, which is still in
# copyright. They now compare the SHA-256 of the output with the SHA-256 of the book's
# expected text, so each rule is exactly as strict without quoting him.

import hashlib
import os
import re
import random
import string
from subprocess import getstatusoutput

prg = './gashlycrumb.py'


# --------------------------------------------------
def file_flag():
    """Either -f or --file"""

    return '-f' if random.randint(0, 1) else '--file'


# --------------------------------------------------
def test_exists():
    """exists"""

    assert os.path.isfile(prg)


# --------------------------------------------------
def test_usage():
    """usage"""

    for flag in ['-h', '--help']:
        rv, out = getstatusoutput(f'{prg} {flag}')
        assert rv == 0
        assert re.match("usage", out, re.IGNORECASE)


# --------------------------------------------------
def test_bad_file():
    """Test for bad --file"""

    bad = random_string()
    letter = random.choice(string.ascii_lowercase)
    rv, out = getstatusoutput(f'{prg} {letter} -f {bad}')
    assert rv != 0
    expected = f"No such file or directory: '{bad}'"
    assert re.search(expected, out)


# --------------------------------------------------
def test_a():
    """Test for 'a'"""

    rv, out = getstatusoutput(f'{prg} a')
    assert rv == 0
    # Amy, and a tumble down the stairs.
    expected = '29a587b6ef262b477ff4e0e4d31e7ea28d76acc757eb87867bc7e39596a4236e'
    assert sha256(out.strip()) == expected


# --------------------------------------------------
def test_b_c():
    """Test for 'b c'"""

    rv, out = getstatusoutput(f'{prg} b c')
    assert rv == 0
    # Basil and some bears, then Clara fading away: two lines.
    expected = '95fe9bcaf5a684073adb20f42994ccab45c2943f4f911832d21fb9b805879956'
    assert sha256(out.strip()) == expected


# --------------------------------------------------
def test_y():
    """Test for 'y'"""

    rv, out = getstatusoutput(f'{prg} Y')
    assert rv == 0
    # Yorick, and a nasty knock on the head.
    expected = 'd31c0de86d8e2fa1587b17a71936b414c2763c4bc58b688db53ca3c7cf83a419'
    assert sha256(out.strip()) == expected


# --------------------------------------------------
def test_o_alternate():
    """ Test for 'o' from 'alternate.txt' """

    rv, out = getstatusoutput(f'{prg} o P q -f alternate.txt')
    assert rv == 0
    expected = ('O is for Orville, who fell in a canyon.\n'
                'P is for Paul, strangled by his banyan.\n'
                'Q is for Quintanna, flayed in the night.')
    assert out.strip() == expected


# --------------------------------------------------
def test_bad_letter():
    """Test for bad input"""

    rv, out = getstatusoutput(f'{prg} 5 CH')
    assert rv == 0
    expected = ('I do not know "5".\n' 'I do not know "CH".')
    assert out.strip() == expected


# --------------------------------------------------
def sha256(text):
    """SHA-256 of text, so a test can check a line without quoting it"""

    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# --------------------------------------------------
def random_string():
    """generate a random string"""

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))
