# Tiny Python Toybox

Little toys, strict rules, sneaky gremlins. Each toy is a program from Ken Youens-Clark's
[*Tiny Python Projects*](https://github.com/kyclark/tiny_python_projects), the book's tests are
its rules, and real-life tests catch what the book's tests miss. Gremlins (mutation testing) show
the difference.

The first screen of every toy shows one recorded moment: the toy passes all the book's rules, a
gremlin changes one thing and still passes them, and a real-life rule catches it. "Run it live"
then runs the same program, tests and gremlins in your browser, in CPython compiled to
WebAssembly (Pyodide).

## Layout

| Path | What |
|---|---|
| `python/upstream/` | The book's tests and input files, unchanged (MIT, with its LICENSE) |
| `python/chapters/` | My programs, real-life tests and property tests, one folder per chapter |
| `python/tptl/` | The harness: in-process `subprocess` shim, mutation testing, metrics |
| `web/` | Next.js static site |
| `web/public/metrics/` | Numbers the site shows, written by CI |
| `docs/` | Plan, the simpler-first-screen notes, and the think-aloud script |

## Commands

```bash
python -m venv .venv && .venv/bin/pip install --group dev
cd python && ../.venv/bin/python -m tptl.metrics ../web/public/metrics   # scores and moments
cd web && npm ci && npm run bundle && npm run build                     # static site in web/out
```

`npm run build` fails if any number or recorded answer on a page doesn't match
`web/public/metrics/`.

Not used from the book: its prose and its solution files. The programs here are written from the
tests.
