"""Real-world cases for wc.py: agree with Unix wc on real files.

The book's inputs are plain ASCII ending in a newline, where counting characters and
counting bytes agree. Logs, CSV exports and text from other people don't play along.
"""

from subprocess import getstatusoutput

prg = "./wc.py"


def counts(path) -> list[int]:
    rv, out = getstatusoutput(f"{prg} {path}")
    assert rv == 0, out
    return [int(x) for x in out.split()[:3]]


def test_utf8_counts_bytes(tmp_path):
    """'café crème' is 13 bytes in UTF-8, as wc -c says, not 11 characters"""
    f = tmp_path / "menu.txt"
    f.write_text("café crème\n", encoding="utf-8")
    assert counts(f) == [1, 2, 13]


def test_no_final_newline(tmp_path):
    """wc counts newlines: a file ending without one has one line fewer"""
    f = tmp_path / "export.csv"
    f.write_bytes(b"id,name\n1,ada")
    assert counts(f) == [1, 2, 13]


def test_windows_line_endings(tmp_path):
    """CRLF files: two lines, and the \\r is a byte too"""
    f = tmp_path / "dos.txt"
    f.write_bytes(b"one\r\ntwo\r\n")
    assert counts(f) == [2, 2, 10]


def test_tabs_and_runs_of_spaces(tmp_path):
    """any run of whitespace separates words"""
    f = tmp_path / "log.tsv"
    f.write_bytes(b"GET\t/index   200\n\n  POST /api\t201  \n")
    assert counts(f) == [3, 6, 36]


def test_missing_file_among_good_ones(tmp_path):
    """like wc: report the missing file, count the rest, and fail at the end"""
    good = tmp_path / "good.txt"
    good.write_text("a b\n")
    rv, out = getstatusoutput(f"{prg} {good} {tmp_path}/missing.txt")
    assert rv != 0
    assert "No such file or directory" in out
    assert f"       1       2       4 {good}" in out


def test_utf8_on_stdin():
    """bytes from a pipe are counted as bytes too"""
    rv, out = getstatusoutput(f"{prg} < ../inputs/fox.txt")
    assert rv == 0
    assert out.split()[:3] == ["1", "9", "45"]
