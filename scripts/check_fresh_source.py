"""Check that a rewritten program is what the next import runs.

Gremlins are written over the program one after another, often at the same size and within
the same second. Python's cached bytecode can't tell those apart, so the tests once ran the
previous gremlin's code and the scores depended on the machine's speed. tptl.mutate's
write_source drops the cache; this fails if it stops doing that.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from tptl.mutate import write_source

with tempfile.TemporaryDirectory() as tmp:
    sys.path.insert(0, tmp)
    sys.dont_write_bytecode = False
    path = str(Path(tmp) / "gremlin.py")
    for value in range(1, 6):
        write_source(path, f"VALUE = {value}\n")  # same size every time, well within a second
        sys.modules.pop("gremlin", None)
        importlib.invalidate_caches()
        got = importlib.import_module("gremlin").VALUE
        if got != value:
            sys.exit(f"Import ran stale code: wrote VALUE = {value}, got {got}")
print("ok: every rewrite was the code that ran")
