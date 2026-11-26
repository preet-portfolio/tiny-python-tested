# mypy: disable-error-code="misc"
# (each mutation site defines its own apply/undo closures with different defaults)
"""Mutation testing small enough to run in a browser.

Each mutant changes one thing in the visitor's program (a comparison, a string, a number,
a method name). We rerun the tests against each mutant: a test that now fails has *killed*
it; a mutant no test kills is a change the spec can't see.

CI also runs mutmut on the reference solutions for the published score; this module is the
interactive version and uses the same idea with fewer operators.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import sys
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass
from typing import Any

from . import shim
from .runner import run_tests

CMP_SWAP: dict[type, type] = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}
BIN_SWAP: dict[type, type] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.FloorDiv,
    ast.Div: ast.Mult,
    ast.FloorDiv: ast.Mult,
    ast.Mod: ast.Mult,
}
METHOD_SWAP = {
    "lower": "upper",
    "upper": "lower",
    "startswith": "endswith",
    "endswith": "startswith",
    "lstrip": "rstrip",
    "rstrip": "lstrip",
    "strip": "lstrip",
    "isupper": "islower",
    "islower": "isupper",
    "append": "remove",
    "sort": "reverse",
    "choice": "choices",
    "title": "lower",
}
# Text that only affects --help output; mutating it shows nothing about behaviour.
COSMETIC_KWARGS = {"help", "description", "epilog", "metavar"}
CRASHED = "(the whole run)"


@dataclass
class Mutant:
    """One single-point change to the program."""

    id: int
    op: str
    line: int
    col: int
    before: str
    after: str
    source: str


def _docstring_nodes(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                ids.add(id(body[0].value))
    return ids


def _cosmetic_nodes(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in COSMETIC_KWARGS:
            for sub in ast.walk(node.value):
                ids.add(id(sub))
    return ids


def _sites(tree: ast.AST) -> Iterator[tuple[str, ast.AST, Callable[[], tuple[str, str]], Callable[[], None]]]:
    """Yield (op, node, apply, undo) for every mutation site."""
    skip = _docstring_nodes(tree) | _cosmetic_nodes(tree)
    # Order matters only where a seeded random function picks from the list.
    random_args = {
        id(a)
        for c in ast.walk(tree)
        if isinstance(c, ast.Call)
        and isinstance(c.func, ast.Attribute)
        and c.func.attr in {"choice", "choices", "sample", "shuffle"}
        for a in c.args
    }

    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in CMP_SWAP:

                    def apply(n=node, i=i, op=op):
                        before = ast.unparse(n)
                        n.ops[i] = CMP_SWAP[type(op)]()
                        return before, ast.unparse(n)

                    def undo(n=node, i=i, op=op):
                        n.ops[i] = op

                    yield "comparison", node, apply, undo
        elif isinstance(node, ast.BoolOp):

            def apply(n=node):
                before = ast.unparse(n)
                n.op = ast.Or() if isinstance(n.op, ast.And) else ast.And()
                return before, ast.unparse(n)

            def undo(n=node, op=node.op):
                n.op = op

            yield "boolean", node, apply, undo
        elif isinstance(node, ast.BinOp) and type(node.op) in BIN_SWAP:

            def apply(n=node):
                before = ast.unparse(n)
                n.op = BIN_SWAP[type(n.op)]()
                return before, ast.unparse(n)

            def undo(n=node, op=node.op):
                n.op = op

            yield "arithmetic", node, apply, undo
        elif isinstance(node, ast.Constant) and not isinstance(node.value, bool):
            v = node.value
            if isinstance(v, str) and v and len(v) < 200:

                def apply(n=node):
                    before = repr(n.value)
                    n.value = "XX" + n.value + "XX"
                    return before, repr(n.value)

                def undo(n=node, v=v):
                    n.value = v

                yield "string", node, apply, undo
            elif isinstance(v, int):

                def apply(n=node):
                    before = repr(n.value)
                    n.value = n.value + 1
                    return before, repr(n.value)

                def undo(n=node, v=v):
                    n.value = v

                yield "number", node, apply, undo
        elif isinstance(node, ast.Attribute) and node.attr in METHOD_SWAP:

            def apply(n=node):
                before = ast.unparse(n)
                n.attr = METHOD_SWAP[n.attr]
                return before, ast.unparse(n)

            def undo(n=node, a=node.attr):
                n.attr = a

            yield "method", node, apply, undo
        elif (
            isinstance(node, (ast.List, ast.Tuple))
            and id(node) in random_args
            and 2 <= len(node.elts) <= 8
            and all(isinstance(e, ast.Constant) for e in node.elts)
            and len({ast.unparse(e) for e in node.elts}) > 1
        ):

            def apply(n=node):
                before = ast.unparse(n)
                n.elts = list(reversed(n.elts))
                return before, ast.unparse(n)

            def undo(n=node, e=tuple(node.elts)):
                n.elts = list(e)

            yield "reverse-list", node, apply, undo
        elif isinstance(node, ast.If):

            def apply(n=node):
                before = "if " + ast.unparse(n.test)
                n.test = ast.UnaryOp(op=ast.Not(), operand=n.test)
                return before, "if " + ast.unparse(n.test)

            def undo(n=node, t=node.test):
                n.test = t

            yield "negate-if", node, apply, undo
        elif isinstance(node, ast.IfExp):

            def apply(n=node):
                before = ast.unparse(n)
                n.body, n.orelse = n.orelse, n.body
                return before, ast.unparse(n)

            def undo(n=node, b=node.body, o=node.orelse):
                n.body, n.orelse = b, o

            yield "swap-branches", node, apply, undo


def generate(source: str, limit: int = 60) -> list[Mutant]:
    """Return up to ``limit`` single-point mutants of ``source``."""
    tree = ast.parse(source)
    mutants: list[Mutant] = []
    for op, node, apply, undo in _sites(tree):
        before, after = apply()
        try:
            mutated = ast.unparse(tree)
        finally:
            undo()
        if before == after:
            continue
        mutants.append(
            Mutant(
                id=len(mutants),
                op=op,
                line=getattr(node, "lineno", 0),
                col=getattr(node, "col_offset", 0),
                before=before[:160],
                after=after[:160],
                source=mutated,
            )
        )
        if len(mutants) >= limit:
            break
    mutants.sort(key=lambda m: (m.line, m.col))
    for i, m in enumerate(mutants):
        m.id = i
    return mutants


def write_source(path: str, text: str) -> None:
    """Replace a program's source and drop its cached bytecode.

    Python trusts a cached .pyc while the source's size and mtime (in whole seconds) match.
    A gremlin is often the same size as the one before it and is written within the same
    second, so without this the tests could run the previous gremlin's code, and how often
    that happened depended on the machine's speed.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    try:
        os.remove(importlib.util.cache_from_source(path))
    except FileNotFoundError:
        pass


def run_mutants(
    chapter_dir: str,
    program: str,
    test_files: list[str],
    limit: int = 60,
    line_budget: int = 200_000,
    progress: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    """Run every mutant against the tests and return the kill matrix."""
    path = os.path.join(chapter_dir, program)
    with open(path, encoding="utf-8") as fh:
        original = fh.read()

    baseline = run_tests(chapter_dir, test_files)
    if baseline["failed"]:
        return {"error": "Mutation testing needs a green suite first.", "baseline": baseline}

    mutants = generate(original, limit)
    rows = []
    shim.LINE_BUDGET = line_budget
    write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        for i, m in enumerate(mutants):
            if progress:
                progress(i, len(mutants))
            write_source(path, m.source)
            res = run_tests(chapter_dir, test_files)
            killers = [t["name"] for t in res["tests"] if t["outcome"] != "passed"]
            # pytest exit codes 2-4 mean the run itself broke (e.g. the mutant exits while
            # a test imports it). Fewer results than the baseline means tests never ran.
            # Either way the mutant was caught, by the suite as a whole.
            if res["exit_code"] in (2, 3, 4) or res["total"] < baseline["total"]:
                killers.append(CRASHED)
            timed_out = any(r["timed_out"] for t in res["tests"] for r in t["runs"])
            row = asdict(m)
            del row["source"]
            row.update({"killed_by": killers, "killed": bool(killers), "timed_out": timed_out})
            rows.append(row)
    finally:
        shim.LINE_BUDGET = None
        sys.dont_write_bytecode = write_bytecode
        write_source(path, original)

    killed = sum(r["killed"] for r in rows)
    return {
        "tests": [t["name"] for t in baseline["tests"]]
        + ([CRASHED] if any(CRASHED in r["killed_by"] for r in rows) else []),
        "mutants": rows,
        "killed": killed,
        "total": len(rows),
        "score": round(killed / len(rows), 4) if rows else None,
    }
