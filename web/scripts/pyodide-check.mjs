// Run every chapter's tests and seeded programs inside Pyodide under Node, and compare with
// real CPython. Catches what only breaks in Pyodide (e.g. sys.prefix is "/" there).
//
//   node scripts/pyodide-check.mjs [--only id1,id2] [--out public/metrics]
//
// Needs `node scripts/fetch-pyodide.mjs` first (it puts the checked wheels in public/pyodide)
// and a native Python 3.14 with pytest and Hypothesis: $PYTHON, default ../.venv/bin/python.
// Loads Pyodide the way public/py-worker.js does: loadPackage for pytest, micropip for the
// pinned Hypothesis wheel, tptl from the same JSON the site ships. One Pyodide instance runs
// every chapter in turn, as one browser tab does.
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadPyodide } from "pyodide";

const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PYODIDE_DIR = path.join(WEB, "public", "pyodide") + path.sep;
const argv = process.argv.slice(2);
const opt = (name, dflt) => (argv.includes(name) ? argv[argv.indexOf(name) + 1] : dflt);
const only = opt("--only", null);
const outDir = path.resolve(WEB, opt("--out", "public/metrics"));
const PYTHON = process.env.PYTHON ?? path.resolve(WEB, "../.venv/bin/python");
const t0 = performance.now();
const secs = (a, b = performance.now()) => Math.round((b - a) / 100) / 10;

if (!existsSync(path.join(PYODIDE_DIR, "extra.json"))) {
  throw new Error("public/pyodide is missing: run `node scripts/fetch-pyodide.mjs` first");
}

// 1. Native CPython: bundles, outcomes, seeded stdout.
const native = JSON.parse(
  execFileSync(PYTHON, [path.join(WEB, "scripts", "pyodide_native.py"), ...(only ? ["--only", only] : [])], {
    maxBuffer: 256 * 1024 * 1024,
    encoding: "utf8",
  }),
);
const tNative = performance.now();
console.log(`native: Python ${native.python}, ${native.chapters.length} chapter(s), ${secs(t0, tNative)}s`);

// 2. Pyodide, set up like the worker.
const py = await loadPyodide({ indexURL: PYODIDE_DIR, stdout: () => {}, stderr: () => {} });
await py.loadPackage(["pytest", "sortedcontainers", "micropip"], { messageCallback: () => {} });
const extra = JSON.parse(readFileSync(path.join(PYODIDE_DIR, "extra.json"), "utf8"));
py.FS.mkdirTree("/wheels");
for (const w of extra) py.FS.writeFile("/wheels/" + w, readFileSync(path.join(PYODIDE_DIR, w)));
{
  const ns = py.toPy({ urls: extra.map((w) => "emfs:/wheels/" + w) });
  await py.runPythonAsync("import micropip\nfor u in urls:\n    await micropip.install(u, deps=False)", { globals: ns });
  ns.destroy();
}
const tptl = Object.fromEntries(
  readdirSync(path.resolve(WEB, "../python/tptl"))
    .filter((f) => f.endsWith(".py"))
    .map((f) => [f, readFileSync(path.resolve(WEB, "../python/tptl", f), "utf8")]),
);
py.FS.mkdirTree("/lib/tptl");
for (const [name, text] of Object.entries(tptl)) py.FS.writeFile("/lib/tptl/" + name, text);
py.runPython("import sys\nsys.path.insert(0, '/lib')\nimport tptl.shim, tptl.runner, tptl.mutate\ntptl.shim.install()");
const pyVersion = py.runPython("import sys; sys.version.split()[0]");
const pyodideVersion = py.version;
const tBoot = performance.now();
console.log(`pyodide ${pyodideVersion}: Python ${pyVersion}, booted in ${secs(tNative, tBoot)}s`);

const normalize = (p) => {
  const out = [];
  for (const part of p.split("/")) {
    if (part === "..") out.pop();
    else if (part && part !== ".") out.push(part);
  }
  return "/" + out.join("/");
};

function callJSON(expr, globals) {
  const ns = py.toPy(globals);
  try {
    return JSON.parse(py.runPython(`import json\njson.dumps(${expr})`, { globals: ns }));
  } finally {
    ns.destroy();
  }
}

// 3. Each chapter: load the bundle as the worker does, run the tests, run the seeds.
const rows = [];
let testMismatches = 0;
let seedMismatches = 0;
for (const ch of native.chapters) {
  const tc = performance.now();
  const dir = "/work/" + ch.id;
  py.runPython(`import shutil; shutil.rmtree("${dir}", ignore_errors=True)`);
  py.FS.mkdirTree(dir);
  for (const [name, text] of Object.entries(ch.bundle.files)) {
    const p = normalize(dir + "/" + name);
    py.FS.mkdirTree(p.slice(0, p.lastIndexOf("/")));
    py.FS.writeFile(p, text);
  }
  py.FS.writeFile(dir + "/" + ch.program, ch.bundle.reference);
  py.FS.chmod(dir + "/" + ch.program, 0o755);

  py.runPython("import tptl.shim as s; s.LINE_BUDGET = 2_000_000");
  let res;
  try {
    res = callJSON("__import__('tptl.runner').runner.run_tests(d, files)", { d: dir, files: ch.files });
  } finally {
    py.runPython("import tptl.shim as s; s.LINE_BUDGET = None");
  }
  const inPyodide = Object.fromEntries(res.tests.map((t) => [t.nodeid, t.outcome]));
  const names = [...new Set([...Object.keys(ch.native), ...Object.keys(inPyodide)])].sort();
  const testDiffs = names
    .filter((n) => ch.native[n] !== inPyodide[n])
    .map((n) => ({
      test: n,
      native: ch.native[n] ?? null,
      pyodide: inPyodide[n] ?? null,
      message: res.tests.find((t) => t.nodeid === n)?.message ?? "",
    }));
  testMismatches += testDiffs.length;

  const seedDiffs = [];
  for (const s of ch.seeded) {
    const r = callJSON(
      `(lambda r: {"status": r.status, "stdout": r.stdout})(__import__('tptl.shim').shim._run_in(d, prog, args))`,
      { d: dir, prog: ch.program, args: s.args },
    );
    const got = Buffer.from(r.stdout, "utf8");
    const want = Buffer.from(s.stdout_b64, "base64");
    if (!got.equals(want) || r.status !== s.status) {
      seedDiffs.push({ args: s.args, native: [s.status, want.toString("utf8")], pyodide: [r.status, r.stdout] });
    }
  }
  seedMismatches += seedDiffs.length;

  const row = {
    chapter: ch.id,
    tests: names.length,
    native_passed: Object.values(ch.native).filter((o) => o === "passed").length,
    pyodide_passed: res.passed,
    mismatches: testDiffs,
    seeded_commands: ch.seeded.length,
    seed_mismatches: seedDiffs.slice(0, 20),
    seconds: secs(tc),
  };
  rows.push(row);
  console.log(
    `${ch.id}: ${row.pyodide_passed}/${row.tests} passed in Pyodide (native ${row.native_passed}), ` +
      `${testDiffs.length} outcome mismatch(es); ${ch.seeded.length} seeded command(s), ` +
      `${seedDiffs.length} differ; ${row.seconds}s`,
  );
  for (const d of testDiffs) console.log(`  test ${d.test}: native ${d.native}, pyodide ${d.pyodide} ${d.message}`);
  for (const d of seedDiffs.slice(0, 5)) console.log(`  seed ${d.args}: ${JSON.stringify(d.native)} vs ${JSON.stringify(d.pyodide)}`);
}

const result = {
  generated: new Date().toISOString().slice(0, 16) + "Z",
  pyodide: pyodideVersion,
  python: { native: native.python, pyodide: pyVersion },
  seeds: native.seeds,
  mismatches: testMismatches,
  seed_mismatches: seedMismatches,
  seconds: { native: secs(t0, tNative), boot: secs(tNative, tBoot), total: secs(t0) },
  rows,
};
if (!only) {
  // A partial run must not overwrite the published file.
  mkdirSync(outDir, { recursive: true });
  writeFileSync(path.join(outDir, "pyodide.json"), JSON.stringify(result, null, 1) + "\n");
}
console.log(
  `total: ${testMismatches} test mismatch(es), ${seedMismatches} seed mismatch(es), ${secs(t0)}s` +
    (only ? " (partial run: pyodide.json not written)" : ""),
);
process.exit(testMismatches || seedMismatches ? 1 : 0);
