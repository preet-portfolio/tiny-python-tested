"""Prove the in-process shim behaves like a real subprocess.

For each chapter and each program (reference solution and starter), run the upstream and
scenario tests twice: once natively with real ``subprocess`` and once through the shim.
Any test whose outcome differs fails the check. Writes metrics/parity.json.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from . import shim, stage
from .runner import run_tests


def native_outcomes(chapter_dir: Path, files: list[str]) -> dict[str, str]:
    """Run pytest in a real subprocess and return {test name: outcome}."""
    report = chapter_dir / ".native.json"
    plugin = Path(__file__).with_name("_report_plugin.py")
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "-p", "tptl._report_plugin", f"--rootdir={chapter_dir}", "-c", os.devnull, *files],
        cwd=chapter_dir,
        env={"TPTL_REPORT": str(report), "PYTHONPATH": str(plugin.parents[1]),
             "PATH": os.path.dirname(os.path.abspath(sys.executable)) + ":/usr/bin:/bin"},
        check=False,
        capture_output=True,
    )
    data = json.loads(report.read_text())
    report.unlink()
    return data


def output_parity(chapter_dir: Path) -> tuple[list[dict], int]:
    """Re-run every command the shim saw through a real shell and compare byte for byte."""
    seen = []
    for r in shim.RECORDER:
        if r.cmd and r.cmd not in seen:
            seen.append(r.cmd)
    env = {"PATH": os.path.dirname(os.path.abspath(sys.executable)) + ":/usr/bin:/bin"}
    diffs = []
    for cmd in seen:
        proc = subprocess.run(cmd, shell=True, cwd=chapter_dir, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        native = (proc.returncode, proc.stdout.removesuffix("\n"))
        cwd = os.getcwd()
        os.chdir(chapter_dir)
        try:
            shimmed = shim.getstatusoutput(cmd)
        finally:
            os.chdir(cwd)
        if native != shimmed:
            diffs.append({"cmd": cmd, "native": list(native), "shim": list(shimmed)})
    return diffs, len(seen)


def main() -> None:
    """Run the parity check over every chapter and write the result."""
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        i = args.index("--only")
        only = set(args[i + 1].split(","))
        del args[i : i + 2]
    out_dir = Path(args[0]) if args else Path("metrics")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    mismatches = 0
    for ch in stage.chapters():
        if only and ch["id"] not in only:
            continue
        files = ch["upstream_tests"] + ch["scenario_tests"]
        sources = {"reference": ch["program"], "starter": "starter.py"}
        if ch.get("book_program"):
            sources["book"] = ch["book_program"]
        for variant, filename in sources.items():
            src = ch["_dir"] / filename
            d = stage.stage(ch, src)
            native = native_outcomes(d, files)
            shimmed = {t["nodeid"]: t["outcome"] for t in run_tests(str(d), files)["tests"]}
            out_diffs, commands = output_parity(d)
            diff = sorted(k for k in native.keys() | shimmed.keys()
                          if native.get(k) != shimmed.get(k))
            mismatches += len(diff) + len(out_diffs)
            rows.append({
                "chapter": ch["id"], "variant": variant, "tests": len(native),
                "native_passed": sum(v == "passed" for v in native.values()),
                "shim_passed": sum(v == "passed" for v in shimmed.values()),
                "commands_compared": commands,
                "mismatches": diff,
                "output_mismatches": out_diffs[:20],
            })
        stage.stage(ch)
    result = {"python": sys.version.split()[0], "mismatches": mismatches, "rows": rows}
    if not only:  # a partial run must not overwrite the published file
        (out_dir / "parity.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))
    sys.exit(1 if mismatches else 0)


if __name__ == "__main__":
    main()
