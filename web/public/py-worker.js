/* Runs CPython (Pyodide) and pytest off the main thread.
 * Messages in:  {id, type: "init" | "load" | "write" | "test" | "run" | "mutate", ...}
 * Messages out: {id, ok, result | error} and {type: "progress", ...}
 */
// Self-hosted (scripts/fetch-pyodide.mjs) so the page needs no third-party runtime.
// Pyodide 314 only runs in module workers.
const PYODIDE = new URL("/pyodide/", self.location.href).href;
let loadPyodide = null;
let bootError = null;
// Not top-level await: the message handler must be attached before the import settles.
const imported = import(PYODIDE + "pyodide.mjs").then(
  (m) => (loadPyodide = m.loadPyodide),
  (err) => (bootError = "Couldn't load Python: " + err.message),
);

let py = null;
let chapterDir = null;
let program = null;

async function init() {
  await imported;
  if (bootError) throw new Error(bootError);
  if (py) return { python: py.runPython("import sys; sys.version.split()[0]") };
  post({ type: "progress", stage: "Downloading Python" });
  py = await loadPyodide({ indexURL: PYODIDE });
  const tptl = await (await fetch("/runtime/tptl.json")).json();
  py.FS.mkdirTree("/lib/tptl");
  for (const [name, text] of Object.entries(tptl)) py.FS.writeFile("/lib/tptl/" + name, text);
  py.runPython(`
import sys
sys.path.insert(0, "/lib")
import tptl.shim
tptl.shim.install()
`);
  return { python: py.runPython("import sys; sys.version.split()[0]") };
}

// pytest, Hypothesis and their dependencies (about 3 MB) load only when someone checks the rules or sends in
// gremlins, so playing with a toy needs just Python itself.
let testsReady = null;
function ensureTests() {
  testsReady ??= (async () => {
    post({ type: "progress", stage: "Loading pytest" });
    await py.loadPackage(["pytest", "sortedcontainers", "micropip"]);
    post({ type: "progress", stage: "Loading Hypothesis" });
    const extra = await (await fetch(PYODIDE + "extra.json")).json();
    const ns = py.toPy({ urls: extra.map((w) => PYODIDE + w) });
    await py.runPythonAsync("import micropip\nfor u in urls:\n    await micropip.install(u, deps=False)", { globals: ns });
    ns.destroy();
    py.runPython("import tptl.runner, tptl.mutate");
  })().catch((err) => {
    testsReady = null;
    throw err;
  });
  return testsReady;
}

function load({ bundle, code }) {
  chapterDir = "/work/" + bundle.id;
  program = bundle.program;
  py.runPython(`import shutil, os; shutil.rmtree("${chapterDir}", ignore_errors=True)`);
  py.FS.mkdirTree(chapterDir);
  for (const [name, text] of Object.entries(bundle.files)) {
    const path = normalize(chapterDir + "/" + name);
    py.FS.mkdirTree(path.slice(0, path.lastIndexOf("/")));
    py.FS.writeFile(path, text);
  }
  write({ name: program, text: code });
  return { dir: chapterDir };
}

function normalize(path) {
  const out = [];
  for (const part of path.split("/")) {
    if (part === "..") out.pop();
    else if (part && part !== ".") out.push(part);
  }
  return "/" + out.join("/");
}

function write({ name, text }) {
  const path = chapterDir + "/" + name;
  py.FS.writeFile(path, text);
  py.FS.chmod(path, 0o755);
  return { written: name };
}

function callJSON(expr, globals) {
  const ns = py.toPy(globals);
  const out = py.runPython(`import json\njson.dumps(${expr})`, { globals: ns });
  ns.destroy();
  return JSON.parse(out);
}

async function test({ files }) {
  await ensureTests();
  // A visitor's infinite loop shouldn't hang the tab: cap lines per program run.
  py.runPython("import tptl.shim as s; s.LINE_BUDGET = 2_000_000");
  try {
    return callJSON("__import__('tptl.runner').runner.run_tests(d, files)", { d: chapterDir, files });
  } finally {
    py.runPython("import tptl.shim as s; s.LINE_BUDGET = None");
  }
}

function run({ args, stdin, prog }) {
  py.runPython("import tptl.shim as s; s.LINE_BUDGET = 2_000_000");
  try {
    return callJSON(
      `(lambda r: {"argv": r.argv, "status": r.status, "stdout": r.stdout, "stderr": r.stderr, "timed_out": r.timed_out})(
         __import__('tptl.shim').shim._run_in(d, prog, args, stdin))`,
      { d: chapterDir, prog: prog ?? program, args, stdin: stdin ?? null },
    );
  } finally {
    py.runPython("import tptl.shim as s; s.LINE_BUDGET = None");
  }
}

async function mutate({ files, limit }) {
  await ensureTests();
  const progress = (i, n) => post({ type: "progress", stage: "mutant", i, n });
  return callJSON(
    "__import__('tptl.mutate').mutate.run_mutants(d, prog, files, limit=limit, progress=progress)",
    { d: chapterDir, prog: program, files, limit: limit ?? 60, progress },
  );
}

const handlers = { init, load, write, test, run, mutate };

function post(msg) {
  self.postMessage(msg);
}

self.onmessage = async (e) => {
  const { id, type, ...args } = e.data;
  try {
    if (type !== "init" && !py) await init();
    const result = await handlers[type](args);
    post({ id, ok: true, result });
  } catch (err) {
    post({ id, ok: false, error: String(err && err.message ? err.message : err) });
  }
};
