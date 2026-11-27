// After `next build`: every number and answer the first screens show must be CI's.
// Fails the build if moments.json disagrees with summary.json, or if a built page doesn't show
// the recorded lines and counts for its toy.
import { readFileSync, existsSync } from "node:fs";

const read = (p) => JSON.parse(readFileSync(p, "utf8"));
const moments = read("public/metrics/moments.json");
const summary = read("public/metrics/summary.json");
const problems = [];
const html = (p) => (existsSync(p) ? readFileSync(p, "utf8") : null);
// The pages hide unsuitable words (lib/kid.ts maskRude); apply the same lists here.
const kid = readFileSync("src/lib/kid.ts", "utf8");
const hiddenWords = new Set(
  [...kid.matchAll(/atob\("([A-Za-z0-9+/=]+)"\)/g)].flatMap((m) => Buffer.from(m[1], "base64").toString().split(",")),
);
const mask = (s) => s.replace(/[A-Za-z]+/g, (w) => (hiddenWords.has(w.toLowerCase()) ? "🙊" : w));
// React escapes text; compare against the same escaping.
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");

for (const c of moments.chapters) {
  const s = summary.chapters.find((x) => x.id === c.id);
  if (!s) {
    problems.push(`${c.id}: in moments.json but not summary.json`);
    continue;
  }
  const want = [
    ["total", s.mutation.book.total, c.gremlins.total],
    ["book caught", s.mutation.book.killed, c.gremlins.book_caught],
    ["all caught", s.mutation.world.killed, c.gremlins.all_caught],
    ["book rules", s.tests.book, c.rules.book],
    ["real-life rules", s.tests.world, c.rules.real_life],
  ];
  for (const [what, a, b] of want) if (a !== b) problems.push(`${c.id}: ${what} is ${b} in moments.json, ${a} in summary.json`);
  // A chip the first screen shows needs words a child can read, not "Go 1"; name it in the
  // chapter's chip_labels when its command is all flags.
  // Same rule as ToyStage: chips that answer, plus the gremlin's chip even when it's refused.
  for (const ch of c.chips)
    if (((ch.status === 0 && ch.stdout.trim()) || ch.args === c.moment?.args) && !ch.label.trim())
      problems.push(`${c.id}: chip “${ch.args}” has no label; add it to chip_labels in its chapter.json`);

  const page = html(`out/chapters/${c.id}/index.html`);
  if (!page) {
    problems.push(`${c.id}: no built page`);
    continue;
  }
  const text = page.replace(/<!-- -->/g, "");
  const must = [
    `passes all ${c.rules.book} of the book`,
    `tests catch ${c.gremlins.book_caught}`,
    `added, ${c.gremlins.all_caught}`,
  ];
  if (c.moment?.real && c.moment?.gremlin) must.push(mask(c.moment.real.line), mask(c.moment.gremlin.line));
  for (const m of must) if (!text.includes(esc(m))) problems.push(`${c.id}: page doesn't show “${m}”`);
}

// The home page shows the toy chosen in src/data/flagship.json, and that toy's recorded gremlin
// must say something wrong (not crash), or the first screen has no guess to make.
const chosen = JSON.parse(readFileSync("src/data/flagship.json", "utf8")).id;
const star = moments.chapters.find((c) => c.id === chosen);
const home = html("out/index.html")?.replace(/<!-- -->/g, "") ?? "";
if (!(star?.moment?.real?.status === 0 && star.moment.gremlin?.status === 0))
  problems.push(`flagship ${chosen} has no recorded gremlin that says something wrong; choose another in src/data/flagship.json`);
else
  for (const m of [mask(star.moment.real.line), mask(star.moment.gremlin.line), `passes all ${star.rules.book} of the book`])
    if (!home.includes(esc(m))) problems.push(`home page doesn't show “${m}”`);

if (problems.length) {
  console.error("check-moments: the pages don't match CI's numbers:\n  " + problems.join("\n  "));
  process.exit(1);
}
console.log(`check-moments: home page and ${moments.chapters.length} toys match CI (${moments.generated}).`);
