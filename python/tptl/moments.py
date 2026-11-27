"""Record each toy's "gremlin moment" for the site's first screen.

The moment: the toy passes every one of the book's rules, a gremlin (one small change) gets
past all of them, and a real-life rule catches it. The site shows it before Python has loaded,
so CI records everything it needs here: the toy's real answers to its example inputs, and the
gremlin's answer to the input where the two differ. Nothing on that screen is typed by hand.
"""

from __future__ import annotations

import ast
import shlex
from pathlib import Path
from typing import Any

from . import shim
from .mutate import CRASHED, generate, write_source
from .runner import repeatable_random

# Which gremlins a child can follow, best first. A changed word or number is easier to explain
# than a flipped branch.
OP_ORDER = ["string", "number", "method", "comparison", "negate-if", "boolean", "arithmetic",
            "swap-branches", "reverse-list"]
MAX_OUT = 2000


def _run(d: Path, program: str, args: str) -> dict[str, Any]:
    # A chip with no --seed ("no seed, different every time") would record new lines on every
    # CI run, and the publish job would commit them though nothing changed. Record it with the
    # tests' fixed seed instead: still a real answer, the same each run, and a gremlin's line
    # then differs from the real one only because of the gremlin. Live play stays random.
    with repeatable_random():
        r = shim._run_in(str(d), program, args)
    return {"status": r.status, "stdout": r.stdout[:MAX_OUT], "stderr": r.stderr[-400:]}


def label(args: str) -> str:
    """What a chip shows: the words, without flags, seeds or folders."""
    out: list[str] = []
    skip = False
    try:
        words = shlex.split(args)
    except ValueError:
        words = args.split()
    for w in words:
        if skip:
            skip = False
            continue
        if w in ("<", "-"):
            continue
        if w.startswith("-"):
            # A flag hides its one value (a seed, a file), except flags that take none and
            # Mad Libs' -i, whose values are the very words the chip should show.
            skip = "=" not in w and w not in ("-l", "--easy", "-i", "--inputs")
            continue
        out.append(Path(w).stem if "/" in w or w.endswith(".txt") else w)
    return " ".join(out)


def _last_line(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[-1] if lines else ""


def _first_difference(a: str, b: str) -> tuple[str, str]:
    """The first line where two outputs differ (the bit worth showing a child)."""
    la, lb = a.splitlines(), b.splitlines()
    for x, y in zip(la, lb):
        if x != y:
            return x, y
    if len(la) != len(lb):
        return (la[len(lb)] if len(la) > len(lb) else ""), (lb[len(la)] if len(lb) > len(la) else "")
    return a, b


def ci_only(d: Path, book_tests: list[str]) -> int:
    """How many of the book's rules the browser skips: they read a text we can't share.

    The chapter's conftest.py names them in NEEDS_TEXT; CI has the text and runs them.
    """
    conf = d / "conftest.py"
    if not conf.exists():
        return 0
    for node in ast.parse(conf.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "NEEDS_TEXT" for t in node.targets):
            names = ast.literal_eval(node.value)
            return sum(1 for t in book_tests if t.rsplit("::", 1)[-1] in names)
    return 0


def record(ch: dict, d: Path, book: dict, world: dict) -> dict[str, Any]:
    """Build one chapter's entry from the two mutation runs (book's rules, then all rules)."""
    program = ch["program"]
    book_tests = [t for t in book.get("tests", []) if t != CRASHED]
    world_tests = [t for t in world.get("tests", []) if t != CRASHED]
    chips = []
    # moment_args, when a chapter has them, are kinder examples for the first screen (Lexi's
    # alphabet instead of the book's gloomy one).
    # chip_labels names chips whose words are all flags ("-s 1 -n 1" would be an empty label).
    named = ch.get("chip_labels", {})
    used = ch.get("moment_args") or ch.get("try_args", [])
    if stale := sorted(set(named) - set(used)):
        raise ValueError(f"{ch['id']}: chip_labels for commands it doesn't run: {stale}")
    for args in used:
        chips.append({"args": args, "label": named.get(args) or label(args), **_run(d, program, args)})

    by_id = {m["id"]: m for m in world.get("mutants", [])}
    escaped = [m for m in book.get("mutants", []) if not m["killed"]]
    caught_later = [m for m in escaped if by_id[m["id"]]["killed"]]
    caught_later.sort(key=lambda m: (OP_ORDER.index(m["op"]) if m["op"] in OP_ORDER else 99, m["id"]))

    moment = None
    if caught_later:
        path = d / program
        original = path.read_text(encoding="utf-8")
        sources = {m.id: m.source for m in generate(original)}
        best = None
        try:
            for m in caught_later:
                write_source(str(path), sources[m["id"]])
                for chip in chips:
                    g = _run(d, program, chip["args"])
                    if g["stdout"] == chip["stdout"] and g["status"] == chip["status"]:
                        continue
                    # Prefer a gremlin that says something wrong over one that crashes.
                    cand = (m, chip, g)
                    if g["status"] == 0 and chip["status"] == 0:
                        best = cand
                        break
                    best = best or cand
                if best and best[2]["status"] == 0 and best[1]["status"] == 0:
                    break
        finally:
            write_source(str(path), original)
        m = best[0] if best else caught_later[0]
        killers = [t for t in by_id[m["id"]]["killed_by"] if t != CRASHED]
        moment = {
            "op": m["op"], "line": m["line"], "before": m["before"], "after": m["after"],
            "caught_by": killers,
            "rules": [ch["rules"].get(t, t.replace("_", " ")) for t in killers],
        }
        if best:
            _, chip, g = best
            real_line, gremlin_line = _first_difference(chip["stdout"], g["stdout"])
            moment.update({
                "args": chip["args"], "label": chip["label"],
                "real": {"status": chip["status"], "line": real_line},
                "gremlin": {"status": g["status"], "line": gremlin_line or _last_line(g["stderr"])},
            })

    return {
        "id": ch["id"],
        "character": ch["character"],
        "rules": {"book": len(book_tests), "real_life": len(world_tests) - len(book_tests),
                  "ci_only": ci_only(d, book_tests)},
        "gremlins": {
            "total": book.get("total", 0),
            "book_caught": book.get("killed", 0),
            "all_caught": world.get("killed", 0),
            "book_missed_real_life_caught": len(caught_later),
        },
        "chips": [{k: c[k] for k in ("args", "label", "status", "stdout")} for c in chips],
        "moment": moment,
    }
