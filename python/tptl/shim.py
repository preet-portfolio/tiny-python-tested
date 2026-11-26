"""Run "./prog.py args < file" in-process, the way subprocess would run it.

The author's tests call ``subprocess.getoutput`` and ``getstatusoutput``. Browsers can't
start processes, so in Pyodide we swap those two functions for the ones below. The parity
check (``tptl.parity``) runs every upstream test both ways and fails on any difference, so
this module has to earn its place rather than be trusted.
"""

from __future__ import annotations

import io
import os
import random
import shlex
import sys
import traceback
import types
from dataclasses import dataclass, field

# A mutant can loop forever; the browser can't kill a worker mid-call cheaply, so the
# mutation runner sets a line budget and this module enforces it with a trace function.
LINE_BUDGET: int | None = None


class BudgetExceeded(Exception):
    """Raised inside the program when it runs more lines than LINE_BUDGET allows."""


@dataclass
class Result:
    """What a process run produced."""

    argv: list[str]
    status: int
    stdout: str
    stderr: str
    stdin: str | bytes | None = None
    timed_out: bool = False
    cmd: str = ""
    # Where in stderr an uncaught traceback starts. CPython flushes stdout before printing
    # one, so that's where stdout lands in the combined stream.
    crash_at: int | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def combined(self) -> str:
        # Piped stdout is block-buffered and stderr is not, so for these small programs a
        # real process shows stderr first and stdout when it exits, except that an uncaught
        # exception flushes stdout before its traceback. Parity checks both.
        if self.crash_at is not None:
            return self.stderr[: self.crash_at] + self.stdout + self.stderr[self.crash_at :]
        return self.stderr + self.stdout


def _parse(cmd: str) -> tuple[list[str], str | None, str | None]:
    """Split a command line into argv, stdin path and stdout path."""
    tokens = shlex.split(cmd)
    argv: list[str] = []
    stdin_path = stdout_path = None
    it = iter(tokens)
    for tok in it:
        if tok == "<":
            stdin_path = next(it)
        elif tok == ">":
            stdout_path = next(it)
        elif tok.startswith("<") and len(tok) > 1:
            stdin_path = tok[1:]
        elif tok in ("2>&1",):
            continue
        else:
            argv.append(tok)
    return argv, stdin_path, stdout_path


class _NamedBytes(io.BytesIO):
    name = "<stdin>"


def _stdin(data: str | bytes) -> io.TextIOWrapper:
    """A text stdin backed by bytes, so sys.stdin.buffer works as it does in a process."""
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return io.TextIOWrapper(_NamedBytes(raw), encoding="utf-8", newline=None)


def run_argv(argv: list[str], stdin_text: str | bytes | None = None) -> Result:
    """Execute argv[0] as __main__ with argv, returning its status and output."""
    prog = argv[0]
    out, err = io.StringIO(), io.StringIO()
    saved = sys.argv, sys.stdin, sys.stdout, sys.stderr
    saved_main = sys.modules.get("__main__")
    rng_state = random.getstate()
    status = 0
    timed_out = False
    crash_at: int | None = None

    try:
        with open(prog, encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        name = os.path.basename(prog)
        return Result(argv, 127, "", f"/bin/sh: {name}: {exc.strerror}\n")

    sys.argv = [prog, *argv[1:]]
    sys.stdin = _stdin(stdin_text or b"")
    sys.stdout, sys.stderr = out, err
    random.seed()  # a fresh process gets a fresh generator

    counter = [0]
    # Python 3.14 joins the cwd and the script path as given, without normalising:
    # "./wc.py" shows up in tracebacks as "/cwd/./wc.py".
    abs_prog = prog if os.path.isabs(prog) else os.path.join(os.getcwd(), prog)

    def tracer(frame, event, arg):
        if event == "line" and frame.f_code.co_filename == abs_prog:
            counter[0] += 1
            if LINE_BUDGET is not None and counter[0] > LINE_BUDGET:
                raise BudgetExceeded(f"stopped after {LINE_BUDGET} lines")
        return tracer

    if LINE_BUDGET is not None:
        sys.settrace(tracer)
    try:
        code = compile(source, abs_prog, "exec")
        # Run as a real __main__ module: argparse (3.14+) reads it to name the program.
        module = types.ModuleType("__main__")
        module.__file__ = prog
        module.__builtins__ = __builtins__  # type: ignore[attr-defined]
        sys.modules["__main__"] = module
        exec(code, module.__dict__)  # noqa: S102 - running the program is the point
    except SystemExit as exc:
        if exc.code is None:
            status = 0
        elif isinstance(exc.code, int):
            status = exc.code
        else:
            print(exc.code, file=err)
            status = 1
    except BudgetExceeded as exc:
        timed_out = True
        print(f"timeout: {exc}", file=err)
        status = 124
    except BaseException as exc:  # noqa: BLE001 - a crashing program is a result
        crash_at = len(err.getvalue())
        tb = exc.__traceback__.tb_next if exc.__traceback__ else None  # hide this frame
        traceback.print_exception(type(exc), exc, tb, file=err)
        status = 1
    finally:
        if LINE_BUDGET is not None:
            sys.settrace(None)
        try:
            out.flush()
        except ValueError:
            pass
        sys.argv, sys.stdin, sys.stdout, sys.stderr = saved
        if saved_main is not None:
            sys.modules["__main__"] = saved_main
        random.setstate(rng_state)

    return Result(
        argv, status & 0xFF, out.getvalue(), err.getvalue(), stdin_text, timed_out,
        crash_at=crash_at,
    )


def run(cmd: str) -> Result:
    """Run a shell-style command line in-process."""
    argv, stdin_path, stdout_path = _parse(cmd)
    stdin_text = None
    if stdin_path is not None:
        with open(stdin_path, "rb") as fh:
            stdin_text = fh.read()
    result = run_argv(argv, stdin_text)
    result.cmd = cmd
    if stdout_path is not None:
        with open(stdout_path, "w", encoding="utf-8") as fh:
            fh.write(result.stdout)
        result.stdout = ""
    return result


def _strip_nl(text: str) -> str:
    # subprocess.getstatusoutput drops exactly one trailing newline
    return text.removesuffix("\n")


def getstatusoutput(cmd: str) -> tuple[int, str]:
    """Drop-in for subprocess.getstatusoutput."""
    result = run(cmd)
    RECORDER.append(result)
    return result.status, _strip_nl(result.combined)


def getoutput(cmd: str) -> str:
    """Drop-in for subprocess.getoutput."""
    return getstatusoutput(cmd)[1]


# Every run made through the shim, so the UI can show the argv/stdout/exit code behind
# each assertion.
RECORDER: list[Result] = []


def install() -> None:
    """Replace subprocess's helpers with the in-process versions."""
    import subprocess

    subprocess.getoutput = getoutput  # type: ignore[assignment]
    subprocess.getstatusoutput = getstatusoutput  # type: ignore[assignment]


def _run_in(directory: str, program: str, args: str, stdin: str | None = None) -> Result:
    """Run ``./program args`` from ``directory`` (the browser terminal); ``< file`` works."""
    cwd = os.getcwd()
    os.chdir(directory)
    try:
        if stdin is not None:
            return run_argv([f"./{program}", *shlex.split(args)], stdin)
        return run(f"./{program} {args}")
    finally:
        os.chdir(cwd)
