// Play one whole turn of each toy, the way a visitor on a cheap phone would, and fail if any
// step doesn't work or axe-core finds a serious accessibility problem.
//
//   node scripts/playthrough.mjs [base URL] [--fast] [--out DIR] [--toys a,b,c]
//
// Default base URL is a local static server on web/out (see the CI job). Each toy gets a
// fresh browser profile (cold cache) with Lighthouse's "slow 4G" and 4x CPU slowdown applied
// to the page *and* to the Web Worker that downloads Python, unless --fast.
// A turn: guess, tap a try chip, read the gremlin, "Run it live", type your own input,
// check the rules, let the gremlins in. Screenshots of every step go to --out.

import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import puppeteer from "puppeteer";
import { AxePuppeteer } from "@axe-core/puppeteer";

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args.splice(i, 2)[1] : undefined;
};
const fast = args.includes("--fast") && args.splice(args.indexOf("--fast"), 1);
const out = flag("--out") ?? "playthrough";
// Twelve Days is here because its scrolling songbook once failed axe and no CI run noticed.
const toys = (flag("--toys") ?? "02_crowsnest,07_gashlycrumb,17_mad_libs,16_scrambler,13_twelve_days").split(",");
const base = (args[0] ?? "http://localhost:4310").replace(/\/$/, "");
mkdirSync(out, { recursive: true });

// Lighthouse's devtools "slow 4G" profile.
const NET = { offline: false, latency: 562.5, downloadThroughput: (1474.56 * 1024) / 8, uploadThroughput: (675 * 1024) / 8 };
const LIVE_TIMEOUT = fast ? 120_000 : 600_000;
// Two rounds of up to 60 gremlins each run in Pyodide; a few minutes even on a fast machine.
const GREMLIN_TIMEOUT = fast ? 900_000 : 2_400_000;

const report = { base, throttled: !fast, toys: [] };
let failed = false;

// protocolTimeout: a gremlin attack is one long wait, longer than Puppeteer's 180 s default per call.
const browser = await puppeteer.launch({ headless: true, args: ["--no-sandbox"], protocolTimeout: GREMLIN_TIMEOUT + 60_000 });
try {
  for (const id of toys) report.toys.push(await play(id));
} finally {
  await browser.close();
}
writeFileSync(path.join(out, "playthrough.json"), JSON.stringify(report, null, 1));
for (const t of report.toys) {
  console.log(`${t.id}: ${t.ok ? "played a whole turn" : "FAILED"} (${t.steps.length} steps)`);
  for (const s of t.steps) console.log(`  ${s.ok ? "✓" : "✗"} ${s.step}${s.ms ? ` ${(s.ms / 1000).toFixed(1)} s` : ""}${s.note ? ` — ${s.note}` : ""}`);
}
process.exit(failed ? 1 : 0);

async function play(id) {
  const ctx = await browser.createBrowserContext();
  const page = await ctx.newPage();
  await page.setViewport({ width: 412, height: 823, deviceScaleFactor: 1.75, isMobile: true, hasTouch: true });
  const problems = [];
  page.on("pageerror", (e) => problems.push(`page error: ${e.message}`));
  page.on("console", (m) => m.type() === "error" && problems.push(`console: ${m.text().slice(0, 200)}`));
  await throttle(page);

  const toy = { id, ok: true, steps: [] };
  const t0 = Date.now();
  const step = async (name, fn) => {
    const s = { step: name };
    const start = Date.now();
    try {
      s.note = (await fn()) ?? undefined;
      s.ms = Date.now() - start;
      const axe = await analyze(page);
      const bad = axe.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
      if (bad.length)
        throw new Error(`axe: ${bad.map((v) => `${v.id} at ${v.nodes.map((n) => n.target.join(" ")).join("; ")}`).join(", ")}`);
      s.ok = true;
    } catch (e) {
      s.ok = false;
      s.ms = Date.now() - start;
      s.note = String(e.message ?? e).slice(0, 300);
      toy.ok = false;
      failed = true;
    }
    await page.screenshot({ path: path.join(out, `${id}-${toy.steps.length + 1}-${name.replace(/\W+/g, "-")}.png`), fullPage: false });
    toy.steps.push(s);
    return s.ok;
  };

  // 1. The first screen, from CI's recording: no Python yet.
  await step("first screen", async () => {
    await page.goto(`${base}/chapters/${id}/`, { waitUntil: "domcontentloaded", timeout: 120_000 });
    await page.waitForSelector(".step .said", { visible: true, timeout: 60_000 });
    return `answer shown after ${((Date.now() - t0) / 1000).toFixed(1)} s`;
  });
  if (await page.$(".guess")) {
    await step("guess", async () => {
      await (await page.$(".guess")).click();
      await page.waitForFunction(() => document.querySelector(".guess-said")?.textContent.trim(), { timeout: 5_000 });
      return text(page, ".guess-said");
    });
  }
  await step("try a chip", async () => {
    const chips = await page.$$(".chip");
    if (chips.length < 1) throw new Error("no chips");
    const pick = chips[Math.min(1, chips.length - 1)];
    await pick.click();
    await page.waitForFunction((el) => el.getAttribute("aria-pressed") === "true", { timeout: 5_000 }, pick);
    return (await text(page, ".step .said")).split("\n")[0];
  });
  await step("gremlin", async () => {
    const s = await text(page, ".step-gremlin");
    if (!/gremlin/i.test(s)) throw new Error("no gremlin section");
    return s.split("\n").find((l) => /caught|rules/.test(l));
  });

  // 2. Run it live: Python wakes up in the browser.
  if (!(await step("run it live", async () => {
    await clickText(page, "button", "Run it live");
    await page.waitForFunction(
      () => document.querySelector(".toy-card") && !document.querySelector(".toy-card .waking") &&
        document.querySelector(".toy-card input, .toy-card textarea, .toy-card button"),
      { timeout: LIVE_TIMEOUT, polling: 500 },
    );
  }))) return finish();

  await step("type your own", async () => {
    const card = await page.$(".toy-card");
    const before = await card.evaluate((el) => el.innerText);
    // Fill the word boxes; use the big text box only when there are none (Mabel's holds her story).
    let fields = await page.$$(".toy-card input[type=text], .toy-card input:not([type])");
    if (!fields.length) fields = await page.$$(".toy-card textarea");
    const words = ["owl", "hat", "pickle", "moon", "giggle", "zebra", "sock", "jelly", "kite", "drum"];
    for (const [i, f] of fields.entries()) {
      await f.click({ clickCount: 3 });
      await f.type(words[i % words.length]);
    }
    // The toy's own "go" button: a form's submit button first, then its big button. Not a chip.
    const go =
      (await page.$(".toy-card form button[type=submit]")) ??
      (await page.$(".toy-card .big-btn")) ??
      (await page.$(".toy-card button"));
    if (!go) throw new Error("no button to press");
    await go.click();
    await page.waitForFunction((b) => document.querySelector(".toy-card").innerText !== b, { timeout: 60_000 }, before);
    return `${fields.length} field(s) typed in`;
  });

  // 3. Peek inside: check the rules, then let the gremlins in.
  await step("check the rules", async () => {
    await page.$eval(".play details.peek", (d) => (d.open = true));
    await (await page.$(".rule-board .big-btn")).click();
    await page.waitForFunction(() => document.querySelectorAll(".rule-score").length > 0, { timeout: LIVE_TIMEOUT, polling: 500 });
    const scores = await page.$$eval(".rule-score", (els) => els.map((e) => e.textContent));
    const skipped = await page.$$eval(".rule.skipped", (els) => els.length);
    const broken = await page.$$eval(".rule.failed", (els) => els.length);
    if (broken) throw new Error(`${broken} rule(s) broken by the real toy`);
    return `book ${scores[0]}, real life ${scores[1]}${skipped ? `, ${skipped} checked on CI only` : ""}`;
  });
  await step("let the gremlins in", async () => {
    await (await page.$(".pit .gremlin-btn")).click();
    // Done when both rounds are tallied (book's rules, then all rules) and the button is free.
    await page.waitForFunction(
      () => {
        const b = document.querySelector(".pit .gremlin-btn");
        return b && !b.disabled && document.querySelectorAll(".pit .tally-row").length >= 2;
      },
      { timeout: GREMLIN_TIMEOUT, polling: 1_000 },
    );
    return (await page.$$eval(".pit .tally-row", (rows) => rows.map((r) => r.innerText.replace(/\s+/g, " ").trim()))).join("; ");
  });
  return finish();

  async function finish() {
    toy.seconds = Math.round((Date.now() - t0) / 1000);
    if (problems.length) {
      toy.problems = problems.slice(0, 10);
      if (problems.some((p) => p.startsWith("page error"))) (toy.ok = false), (failed = true);
    }
    await ctx.close();
    return toy;
  }
}

// axe needs a settled frame; right after navigation it can report "not ready", so retry.
async function analyze(page) {
  for (let i = 0; ; i++) {
    try {
      return await new AxePuppeteer(page).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    } catch (e) {
      if (i >= 10 || !/not ready|detached|navigat/i.test(String(e))) throw e;
      await new Promise((r) => setTimeout(r, 1_000));
    }
  }
}

async function throttle(page) {
  const cdp = await page.createCDPSession();
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  if (fast) return;
  await cdp.send("Network.emulateNetworkConditions", NET);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  // Python downloads in a Web Worker: pause each worker as it starts, throttle it, resume it.
  await cdp.send("Target.setAutoAttach", { autoAttach: true, waitForDebuggerOnStart: true, flatten: true });
  cdp.on("Target.attachedToTarget", async ({ sessionId }) => {
    const ws = cdp.connection().session(sessionId);
    if (!ws) return;
    await ws.send("Network.enable").catch(() => {});
    await ws.send("Network.emulateNetworkConditions", NET).catch(() => {});
    await ws.send("Runtime.runIfWaitingForDebugger").catch(() => {});
  });
}

function text(page, sel) {
  return page.$eval(sel, (e) => e.innerText.trim());
}

async function clickText(page, tag, words) {
  const els = await page.$$(tag);
  for (const el of els) {
    if ((await el.evaluate((e) => e.innerText)).includes(words)) return el.click();
  }
  throw new Error(`no ${tag} saying "${words}"`);
}
