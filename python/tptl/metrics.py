"""Measure every chapter and write the numbers the site shows.

Writes <out>/summary.json and <out>/moments.json (see moments.py): per chapter, test counts and in-browser-style mutation scores
for the book's tests alone and with the real-world tests, from the reference solution.
CI adds mutmut and coverage beside it. Nothing on the site is typed by hand.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from . import moments, stage
from .mutate import run_mutants
from .runner import run_tests


def measure(ch: dict) -> tuple[dict, dict]:
    """One chapter's scores and gremlin moment."""
    d = str(stage.stage(ch))
    book, world = ch["upstream_tests"], ch["upstream_tests"] + ch["scenario_tests"]
    res = run_tests(d, world)
    m_book = run_mutants(d, ch["program"], book)
    m_world = run_mutants(d, ch["program"], world)
    row = {
        "id": ch["id"],
        "tests": {"book": sum(t["file"] in book for t in res["tests"]),
                  "world": sum(t["file"] in ch["scenario_tests"] for t in res["tests"]),
                  "passed": res["passed"], "total": res["total"]},
        "mutation": {
            "book": {"killed": m_book["killed"], "total": m_book["total"]},
            "world": {"killed": m_world["killed"], "total": m_world["total"]},
        },
    }
    return row, moments.record(ch, Path(d), m_book, m_world)


def main() -> None:
    """Measure all chapters, each in a fresh Python process."""
    if sys.argv[1:2] == ["--chapter"]:
        # Child process: measure one chapter and write the result to a file.
        ch = next(c for c in stage.chapters() if c["id"] == sys.argv[2])
        Path(sys.argv[3]).write_text(json.dumps(measure(ch)))
        return
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("metrics")
    out.mkdir(parents=True, exist_ok=True)
    chapters = []
    found = []
    # A fresh process per chapter, as the browser has a fresh Python per page. In one long
    # process, state left by earlier chapters' gremlins changed later counts by one or two.
    with tempfile.TemporaryDirectory() as tmp:
        for ch in stage.chapters():
            result = Path(tmp) / f"{ch['id']}.json"
            subprocess.run([sys.executable, "-m", "tptl.metrics", "--chapter", ch["id"], str(result)],
                           check=True, stdout=subprocess.DEVNULL)
            row, moment = json.loads(result.read_text())
            chapters.append(row)
            found.append(moment)
            print(ch["id"], row["mutation"], flush=True)
    summary = {
        "generated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "python": sys.version.split()[0],
        "chapters": chapters,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    (out / "moments.json").write_text(json.dumps(
        {"generated": summary["generated"], "python": summary["python"], "chapters": found},
        indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
