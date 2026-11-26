"""Run a chapter's tests in-process and return structured results.

Used by the browser worker and by the parity check, so both read the same shape.
"""

from __future__ import annotations

import contextlib
import io
import os
import random
import sys
import sysconfig
from typing import Any

from . import shim


class _Collector:
    """pytest plugin that records one row per test."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self._runs_at_start = 0

    def pytest_runtest_setup(self, item: Any) -> None:
        self._runs_at_start = len(shim.RECORDER)
        # The book's tests draw random words, seeds and boards. Seeding per test (by name, so
        # order doesn't matter) makes every run, and every gremlin count, the same.
        random.seed(f"tptl:{item.nodeid}")

    def pytest_runtest_logreport(self, report: Any) -> None:
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
            runs = shim.RECORDER[self._runs_at_start :]
            self.rows.append(
                {
                    "nodeid": report.nodeid,
                    "name": report.nodeid.split("::")[-1],
                    "file": report.nodeid.split("::")[0],
                    "outcome": report.outcome,
                    "duration": round(report.duration, 4),
                    "message": _short(report) if report.failed else "",
                    "detail": report.longreprtext if report.failed else "",
                    "runs": [
                        {
                            "argv": r.argv,
                            "status": r.status,
                            "stdout": r.stdout[-4000:],
                            "stderr": r.stderr[-4000:],
                            "timed_out": r.timed_out,
                        }
                        for r in runs[-3:]
                    ],
                    "run_count": len(runs),
                }
            )


def _short(report: Any) -> str:
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is not None:
        return str(crash.message).splitlines()[0][:300]
    return report.longreprtext.strip().splitlines()[-1][:300] if report.longreprtext else ""


# Where libraries live. Not sys.prefix: in Pyodide that is "/", which contains everything.
_LIBRARY_DIRS = tuple(
    sorted(
        {
            os.path.join(p, "")
            for p in (
                *(sysconfig.get_paths().get(k) for k in ("stdlib", "platstdlib", "purelib", "platlib")),
                os.path.dirname(__file__),
            )
            if p and len(p) > 1
        }
    )
)


def _forget_new(before: set[str]) -> None:
    """Drop modules a run imported from user space (tests, programs), keeping libraries.

    Every chapter's tests live in a file called test.py, so a cached module from one run
    would otherwise answer for the next chapter's tests.
    """
    for name in set(sys.modules) - before:
        path = getattr(sys.modules[name], "__file__", None) or ""
        if path and not path.startswith(_LIBRARY_DIRS):
            del sys.modules[name]


def run_tests(chapter_dir: str, files: list[str], extra_args: list[str] | None = None) -> dict:
    """Run pytest on ``files`` inside ``chapter_dir`` through the shim."""
    import pytest

    shim.install()
    shim.RECORDER.clear()
    collector = _Collector()
    cwd = os.getcwd()
    os.chdir(chapter_dir)
    before = set(sys.modules)
    log = io.StringIO()
    # A program run without --seed calls random.seed(None), which reads the OS clock. Under
    # test, map that to a fixed seed so results repeat; toy runs keep real randomness.
    real_seed = random.seed

    def _repeatable_seed(a: Any = None, version: int = 2) -> None:
        real_seed("tptl:unseeded" if a is None else a, version)

    random.seed = _repeatable_seed  # type: ignore[assignment]
    # Some tests call a program's main() in-process, which reads sys.argv. Give them a clean
    # one, or the result depends on how this runner was started (CI script, browser, pytest).
    real_argv = sys.argv
    sys.argv = ["pytest"]
    try:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = pytest.main(
                [
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    f"--rootdir={os.path.abspath(chapter_dir)}",
                    "-c",
                    os.devnull,
                    *(extra_args or []),
                    *files,
                ],
                plugins=[collector],
            )
    finally:
        random.seed = real_seed  # type: ignore[assignment]
        sys.argv = real_argv
        os.chdir(cwd)
        _forget_new(before)
    rows = collector.rows
    return {
        "exit_code": int(code),
        "passed": sum(r["outcome"] == "passed" for r in rows),
        "failed": sum(r["outcome"] == "failed" for r in rows),
        "total": len(rows),
        "tests": rows,
        "log": log.getvalue()[-6000:],
    }
