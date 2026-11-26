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

// The home page shows the flagship (same rule as flagship() in src/lib/data.ts).
const star = moments.chapters
  .filter((c) => c.moment?.real?.status === 0 && c.moment?.gremlin?.status === 0)
  .sort((a, b) => b.gremlins.book_missed_real_life_caught - a.gremlins.book_missed_real_life_caught)[0];
const home = html("out/index.html")?.replace(/<!-- -->/g, "") ?? "";
if (star)
  for (const m of [mask(star.moment.real.line), mask(star.moment.gremlin.line), `passes all ${star.rules.book} of the book`])
    if (!home.includes(esc(m))) problems.push(`home page doesn't show “${m}”`);

if (problems.length) {
  console.error("check-moments: the pages don't match CI's numbers:\n  " + problems.join("\n  "));
  process.exit(1);
}
console.log(`check-moments: home page and ${moments.chapters.length} toys match CI (${moments.generated}).`);
