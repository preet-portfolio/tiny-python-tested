"""Real-world cases for howler.py: normalising a file or a pipe.

A text tool earns its keep in a pipeline: `cat notes.txt | howler.py - -o loud.txt`. Real files
come from Windows Notepad with an invisible mark at the start, and output paths have typos.
Every case here must pass without breaking a single test in the author's test.py.
"""

import os
from subprocess import getstatusoutput

prg = "./howler.py"
fox = "../inputs/fox.txt"
FOX = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG."


def write(name: str, data: bytes) -> str:
    with open(name, "wb") as fh:
        fh.write(data)
    return name


def test_reads_a_pipe():
    """'-' means: read what's piped in"""
    rv, out = getstatusoutput(f"{prg} - < {fox}")
    assert rv == 0
    assert out == FOX


def test_pipe_into_a_file():
    """read a pipe, write a file"""
    try:
        rv, out = getstatusoutput(f"{prg} -o piped.txt - < {fox}")
        assert rv == 0 and out == ""
        with open("piped.txt", encoding="utf-8") as fh:
            assert fh.read() == FOX + "\n"
    finally:
        if os.path.exists("piped.txt"):
            os.remove("piped.txt")


def test_notepad_mark_is_dropped():
    """the invisible mark at the start of a Notepad file doesn't come along"""
    # Not removed afterwards: a piped command needs its file whenever it is replayed.
    name = write("notepad.txt", "﻿hello there\r\n".encode())
    for args in (name, f"- < {name}"):
        rv, out = getstatusoutput(f"{prg} {args}")
        assert rv == 0
        assert out == "HELLO THERE"


def test_bad_output_folder_is_a_polite_error():
    """a typo in the output folder gets a message, not a crash"""
    rv, out = getstatusoutput(f"{prg} -o no/such/folder/out.txt 'hi'")
    assert rv != 0
    assert "Traceback" not in out
    assert "no/such/folder/out.txt" in out


def test_keeps_every_line():
    """blank lines in the middle stay where they are"""
    name = write("lines.txt", b"one\n\ntwo\nthree\n")
    try:
        rv, out = getstatusoutput(f"{prg} {name}")
        assert rv == 0
        assert out == "ONE\n\nTWO\nTHREE"
    finally:
        os.remove(name)


def test_shouting_twice_changes_nothing():
    """shouting something already shouted gives the same thing"""
    try:
        getstatusoutput(f"{prg} -o once.txt {fox}")
        rv, out = getstatusoutput(f"{prg} once.txt")
        assert rv == 0
        assert out == FOX
    finally:
        if os.path.exists("once.txt"):
            os.remove("once.txt")
