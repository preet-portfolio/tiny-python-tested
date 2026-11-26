"""Run every chapter's book and real-world tests natively, with real subprocesses.

Each chapter runs in its own build directory with the same pytest invocation as
tptl.parity.native_outcomes (--rootdir=<dir>, -c os.devnull), so the book's tests see the
layout they were written for: ./prog.py beside test.py, inputs in ../inputs.

    python scripts/native_tests.py [--only id1,id2] [--build DIR] [--coverage OUT_DIR]

--build stages into DIR instead of python/build (use a temporary folder when others share
python/build). --coverage measures the reference solutions, including the runs the tests
start through subprocess (coverage's `patch = subprocess`), and writes OUT_DIR/coverage.json.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(ROOT))

from tptl import stage


def _opt(args: list[str], name: str) -> str | None:
    return args[args.index(name) + 1] if name in args else None


def main() -> None:
    args = sys.argv[1:]
    only = _opt(args, "--only")
    ids = set(only.split(",")) if only else None
    build = _opt(args, "--build")
    cov_out = _opt(args, "--coverage")
    if build:
        stage.BUILD = Path(build).resolve()
    bindir = os.path.dirname(os.path.abspath(sys.executable))
    env = {**os.environ, "PATH": bindir + os.pathsep + os.environ.get("PATH", "")}
    tmp = Path(tempfile.mkdtemp(prefix="tptl-cov-")).resolve()
    failed: list[str] = []
    rows = []
    for ch in stage.chapters():
        if ids and ch["id"] not in ids:
            continue
        d = stage.stage(ch)
        files = ch["upstream_tests"] + ch["scenario_tests"]
        pytest = ["-m", "pytest", "-q", "-p", "no:cacheprovider", f"--rootdir={d}", "-c",
                  os.devnull, *files]
        print(f"== {ch['id']}: {' '.join(files)}", flush=True)
        if not cov_out:
            r = subprocess.run([sys.executable, *pytest], cwd=d, env=env, check=False)
            if r.returncode:
                failed.append(ch["id"])
            continue
        rc = tmp / f"{ch['id']}.coveragerc"
        data = tmp / f"{ch['id']}.coverage"
        rc.write_text(
            "[run]\nbranch = true\nparallel = true\npatch = subprocess\n"
            f"data_file = {data}\ninclude = {d / ch['program']}\n"
        )
        r = subprocess.run([sys.executable, "-m", "coverage", "run", f"--rcfile={rc}", *pytest],
                           cwd=d, env=env, check=False)
        if r.returncode:
            failed.append(ch["id"])
        subprocess.run([sys.executable, "-m", "coverage", "combine", f"--rcfile={rc}", "-q"],
                       cwd=d, env=env, check=True)
        report = tmp / f"{ch['id']}.json"
        subprocess.run([sys.executable, "-m", "coverage", "json", f"--rcfile={rc}", "-q",
                        "-o", str(report)], cwd=d, env=env, check=True)
        totals = json.loads(report.read_text())["totals"]
        rows.append({
            "id": ch["id"], "program": ch["program"],
            "statements": totals["num_statements"], "covered": totals["covered_lines"],
            "branches": totals.get("num_branches", 0),
            "covered_branches": totals.get("covered_branches", 0),
            "percent": round(totals["percent_covered"], 1),
        })
        print(f"   coverage {rows[-1]['percent']}%", flush=True)
    if cov_out and not ids:  # a partial run must not overwrite the published file
        out = Path(cov_out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "coverage.json").write_text(json.dumps({
            "generated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ"),
            "python": sys.version.split()[0],
            "tests": "book + real world, real subprocess",
            "chapters": rows,
        }, indent=1) + "\n")
    if cov_out:
        print(json.dumps(rows, indent=1))
    if failed:
        print("failed: " + ", ".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
