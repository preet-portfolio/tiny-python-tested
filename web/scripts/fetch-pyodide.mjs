// Self-host Pyodide: copy the core from node_modules and download only the wheels pytest
// needs (with their dependencies), checked against the SHA-256 in pyodide-lock.json.
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const SRC = "node_modules/pyodide";
const OUT = "public/pyodide";
const VERSION = JSON.parse(readFileSync(path.join(SRC, "package.json"), "utf8")).version;
const CDN = `https://cdn.jsdelivr.net/pyodide/v${VERSION}/full/`;
const WANT = ["pytest", "sortedcontainers", "micropip"];
// Not in Pyodide's lock file: pinned from PyPI, built for this Pyodide ABI.
const EXTRA = [
  {
    file: "hypothesis-6.170.15-cp314-cp314-pyemscripten_2026_0_wasm32.whl",
    url: "https://files.pythonhosted.org/packages/2b/08/500fbe05990d886d4502fa334f6cf03607be473b2a2efffb660238135f05/hypothesis-6.170.15-cp314-cp314-pyemscripten_2026_0_wasm32.whl",
    sha256: "1138c03edf4c4401afb28e50255644b4ab4e1ad52864456cd4e84458ba8c671a",
  },
];

mkdirSync(OUT, { recursive: true });
for (const f of ["pyodide.js", "pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]) {
  copyFileSync(path.join(SRC, f), path.join(OUT, f));
}

const lock = JSON.parse(readFileSync(path.join(SRC, "pyodide-lock.json"), "utf8"));
const need = new Set();
const visit = (name) => {
  const key = name.toLowerCase();
  if (need.has(key)) return;
  const pkg = lock.packages[key];
  if (!pkg) throw new Error(`Not in the Pyodide lock file: ${name}`);
  need.add(key);
  (pkg.depends ?? []).forEach(visit);
};
WANT.forEach(visit);

const downloads = [
  ...[...need].map((key) => ({ file: lock.packages[key].file_name, url: CDN + lock.packages[key].file_name, sha256: lock.packages[key].sha256 })),
  ...EXTRA,
];
for (const { file: file_name, url, sha256 } of downloads) {
  const dest = path.join(OUT, file_name);
  if (existsSync(dest) && createHash("sha256").update(readFileSync(dest)).digest("hex") === sha256) continue;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${file_name}: HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const got = createHash("sha256").update(buf).digest("hex");
  if (got !== sha256) throw new Error(`${file_name}: checksum mismatch`);
  writeFileSync(dest, buf);
}
writeFileSync(path.join(OUT, "extra.json"), JSON.stringify(EXTRA.map((e) => e.file)));
console.log(`Pyodide ${VERSION}: core + ${[...need].join(", ")} + ${EXTRA.map((e) => e.file).join(", ")}`);
