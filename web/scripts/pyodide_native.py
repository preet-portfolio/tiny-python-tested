"""Native side of scripts/pyodide-check.mjs: what real CPython says, for Pyodide to match.

Prints one JSON object on stdout: per chapter, the browser bundle (stage.bundle, the same
files the site ships), the test outcomes from a real subprocess run (tptl.parity), and for
seeded programs the stdout of a fixed list of seeded commands run through a real shell.

Chapters are staged in a temporary directory, not python/build, so this can run while
other work uses the shared build folder.

    python scripts/pyodide_native.py [--only id1,id2]
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "python"
sys.path.insert(0, str(ROOT))

from tptl import parity, stage

SEEDS = [0, 1, 2, 3, 7, 42, 1000, 123456789]
SEED_FLAG = re.compile(r"(?<!\S)(-s|--seed)(\s+|=)(\d+)")
# Extra text for seeded programs that take text: non-ASCII, case-changing and wide chars.
EXTRA_TEXT = "'Ünïcödé Straße İstanbul ǅ 🐱 café'"


def takes_seed(d: Path, program: str, env: dict[str, str]) -> bool:
    """True when the program's --help lists -s/--seed."""
    out = subprocess.run(f"./{program} --help", shell=True, cwd=d, env=env, text=True,
                         capture_output=True, check=False).stdout
    return bool(re.search(r"(^|\s)(-s|--seed)\b", out))


def seeded_commands(ch: dict) -> list[str]:
    """A fixed list: every seeded try_args template (or "-s N") times SEEDS."""
    templates = [a for a in ch.get("try_args", []) if SEED_FLAG.search(a)]
    if not templates:
        templates = [f"-s 1 {a}".strip() for a in ch.get("try_args", [])] or ["-s 1"]
    if any("'" in t for t in templates):  # the program takes free text
        templates.append(f"-s 1 {EXTRA_TEXT}")
    cmds = []
    for t in templates:
        for s in SEEDS:
            cmd = SEED_FLAG.sub(rf"\g<1>\g<2>{s}", t, count=1)
            if cmd not in cmds:
                cmds.append(cmd)
    return cmds


def main() -> None:
    args = sys.argv[1:]
    only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
    env = {"PATH": os.path.dirname(os.path.abspath(sys.executable)) + ":/usr/bin:/bin",
           "PYTHONIOENCODING": "utf-8", "LC_ALL": "C.UTF-8"}
    rows: list[dict] = []
    out = {"python": sys.version.split()[0], "seeds": SEEDS, "chapters": rows}
    with tempfile.TemporaryDirectory(prefix="tptl-native-") as tmp:
        # Resolved: on macOS /var is a symlink, and pytest node ids need the real path.
        stage.BUILD = Path(tmp).resolve()
        for ch in stage.chapters():
            if only and ch["id"] not in only:
                continue
            d = stage.stage(ch)
            files = ch["upstream_tests"] + ch["scenario_tests"]
            row: dict = {
                "id": ch["id"],
                "program": ch["program"],
                "files": files,
                "bundle": stage.bundle(ch),
                "native": parity.native_outcomes(d, files),
                "seeded": [],
            }
            if takes_seed(d, ch["program"], env):
                for args_ in seeded_commands(ch):
                    p = subprocess.run(f"./{ch['program']} {args_}", shell=True, cwd=d, env=env,
                                       capture_output=True, check=False)
                    row["seeded"].append({
                        "args": args_,
                        "status": p.returncode,
                        "stdout_b64": base64.b64encode(p.stdout).decode(),
                        "sha256": hashlib.sha256(p.stdout).hexdigest(),
                    })
            rows.append(row)
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
