"""pytest plugin: write {nodeid: outcome} to $TPTL_REPORT (used by the parity check)."""

import json
import os

_rows: dict[str, str] = {}


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        _rows[report.nodeid] = report.outcome


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get("TPTL_REPORT")
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(_rows, fh)
