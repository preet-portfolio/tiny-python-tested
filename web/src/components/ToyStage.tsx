"use client";

import dynamic from "next/dynamic";
import { useRef, useState } from "react";
import { Gremlin } from "./Gremlin";
import type { BrainId } from "./Playground";
import { gremlinDid, maskRude } from "@/lib/kid";
import type { MomentEntry } from "@/lib/data";
import type { Bundle } from "@/lib/py";

// Python, the editor and the toys only load when someone asks to run it live.
const Playground = dynamic(() => import("./Playground").then((m) => m.Playground), {
  ssr: false,
  loading: () => (
    <p className="waking" role="status">
      Waking up…
    </p>
  ),
});

const SHOWN_LINES = 8;
const NOTHING = "(says nothing)";
const line = (text: string) => maskRude(text) || NOTHING;

function clip(text: string) {
  const lines = maskRude(text).replace(/\n$/, "").split("\n");
  return lines.length > SHOWN_LINES ? [...lines.slice(0, SHOWN_LINES), "…"].join("\n") : lines.join("\n");
}

const testNames = (source: string) => [...source.matchAll(/^def (test_\w+)/gm)].map((m) => m[1]);

function day(iso: string) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}

/**
 * One toy's first screen: guess, try, see the gremlin. Everything on it comes from CI's
 * recording (moments.json), so it shows before Python has loaded. "Run it live" loads Python.
 */
export function ToyStage({
  bundle,
  entry,
  generated,
  python,
  headingLevel = 2,
}: {
  bundle: Bundle;
  entry: MomentEntry;
  generated: string;
  python: string;
  headingLevel?: 1 | 2;
}) {
  const who = entry.character.name;
  const m = entry.moment;
  const show = m?.real && m.gremlin ? { real: m.real, gremlin: m.gremlin, label: m.label ?? "" } : null;
  // The first screen shows answers, not error messages (those are for running it live),
  // and one chip per label (two examples can differ only in a flag a child doesn't see).
  const chips = entry.chips
    .filter((c) => (c.status === 0 && c.stdout.trim()) || c.args === m?.args)
    .filter((c, i, all) => all.findIndex((x) => x.label === c.label) === i || c.args === m?.args);
  const startChip = Math.max(0, chips.findIndex((c) => c.args === m?.args));
  const [chip, setChip] = useState(startChip);
  const [guess, setGuess] = useState<"real" | "gremlin" | null>(null);
  const [live, setLive] = useState(false);
  const [brainRequest, setBrainRequest] = useState<{ brain: BrainId; n: number } | undefined>();
  const liveRef = useRef<HTMLDivElement>(null);
  const { book, real_life } = entry.rules;
  const g = entry.gremlins;
  const H = headingLevel === 1 ? "h1" : "h2";

  // Show the two answers in a fixed order that doesn't give the right one away.
  const options = show
    ? [...([
        ["real", show.real.line],
        ["gremlin", show.gremlin.line],
      ] as const)].sort((a, b) => a[1].localeCompare(b[1]))
    : [];

  const goLive = (brain?: BrainId) => {
    setLive(true);
    if (brain) setBrainRequest((r) => ({ brain, n: (r?.n ?? 0) + 1 }));
    requestAnimationFrame(() => liveRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
  };

  const bookTests = bundle.upstream_tests.flatMap((f) => testNames(bundle.files[f] ?? ""));
  const realTests = bundle.scenario_tests.flatMap((f) => testNames(bundle.files[f] ?? ""));
  const shown = chips[chip];

  return (
    <div className="stage">
      <header className="stage-head">
        <span className="ch-face" aria-hidden="true">
          {entry.character.emoji}
        </span>
        <div>
          <H className="stage-name">{who}</H>
          <p className="ch-role">{entry.character.role}</p>
        </div>
      </header>

      {show && show.gremlin.status === 0 && (
        <section className="step" aria-labelledby={`${entry.id}-guess`}>
          <h3 id={`${entry.id}-guess`} className="step-h">
            Guess
          </h3>
          <p className="step-q">
            {show.label ? (
              <>
                What will {who} say for <strong>“{show.label}”</strong>?
              </>
            ) : (
              <>What will {who} say?</>
            )}
          </p>
          <div className="guesses">
            {options.map(([kind, text]) => (
              <button
                key={kind}
                type="button"
                className={`guess${guess === kind ? (kind === "real" ? " right" : " wrong") : ""}`}
                aria-pressed={guess === kind}
                onClick={() => setGuess(kind)}
              >
                {line(text)}
              </button>
            ))}
          </div>
          <p className="guess-said" aria-live="polite">
            {guess === "real" && <>Yes! That&apos;s what {who} says.</>}
            {guess === "gremlin" && <>Nope. That&apos;s what a gremlin makes {who} say. Look below!</>}
          </p>
        </section>
      )}

      <section className="step" aria-labelledby={`${entry.id}-try`}>
        <h3 id={`${entry.id}-try`} className="step-h">
          Try
        </h3>
        {chips.length > 0 && (
          <>
            <div className="chips" role="group" aria-label={`Things to give ${who}`}>
              {chips.map((c, i) => (
                <button
                  key={c.args}
                  type="button"
                  className="chip"
                  aria-pressed={i === chip}
                  onClick={() => setChip(i)}
                >
                  {c.label || `Go ${i + 1}`}
                </button>
              ))}
            </div>
            {shown && (
              <pre className={`said${shown.status === 0 ? "" : " said-bad"}`} aria-live="polite">
                {clip(shown.stdout) || NOTHING}
              </pre>
            )}
          </>
        )}
        <p className="ticks">
          <span className="tick">✓</span> {who} passes all {book} of the book&apos;s rules
          {real_life > 0 && <> and all {real_life} real-life rules</>}.
        </p>
      </section>

      <section className="step step-gremlin" aria-labelledby={`${entry.id}-gremlin`}>
        <h3 id={`${entry.id}-gremlin`} className="step-h">
          Gremlin!
        </h3>
        {m ? (
          <>
            <p className="g-did">
              <Gremlin mood="sneaky" className="g-inline" />A gremlin {gremlinDid(m.op)} in {who}&apos;s head.
            </p>
            {show && (
              <dl className="versus">
                <dt>{who}</dt>
                <dd className="said">{line(show.real.line)}</dd>
                <dt>Gremlin {who}</dt>
                <dd className="said said-bad">
                  {show.gremlin.status === 0 ? line(show.gremlin.line) : `💥 crashes: ${maskRude(show.gremlin.line)}`}
                </dd>
              </dl>
            )}
            <ul className="verdicts">
              <li>
                <span className="tick">✓</span> The book&apos;s {book} rules all still pass. They didn&apos;t spot it.
              </li>
              <li>
                <span className="cross">✗</span> A real-life rule caught it
                {m.rules[0] ? <>: <span className="rule-quote">{maskRude(m.rules[0])}</span></> : "!"}
              </li>
            </ul>
          </>
        ) : (
          <p>
            Gremlins changed {who} in {g.total} ways. The book&apos;s {book} rules caught {g.book_caught} of them
            {g.all_caught === g.book_caught ? ". The real-life rules didn't catch any more." : "."}
          </p>
        )}
        <p className="recorded">
          Saved from a real run on {day(generated)}.
        </p>
      </section>

      {!live && (
        <p className="go-live">
          <button type="button" className="big-btn" onClick={() => goLive()}>
            ▶ Run it live
          </button>
          <small>Wakes up a real Python in your browser. Type your own words, and send in all the gremlins.</small>
        </p>
      )}

      <div ref={liveRef}>{live && <Playground bundle={bundle} brainRequest={brainRequest} />}</div>

      {!live && (
        <details className="peek">
          <summary>
            Peek inside <span>(the gremlin&apos;s trick, and every rule)</span>
          </summary>
          <div className="peek-body">
            {m && (
              <p>
                The gremlin changed line {m.line} of <code>{bundle.program}</code>: <code className="was">{m.before}</code>{" "}
                <span aria-hidden="true">→</span> <code className="now">{m.after}</code>
              </p>
            )}
            <h3>The book&apos;s rules</h3>
            <ul className="rules-plain">
              {bookTests.map((t) => (
                <li key={t}>{bundle.rules[t] ?? t.replace(/_/g, " ")}</li>
              ))}
            </ul>
            <h3>Real-life rules</h3>
            <ul className="rules-plain">
              {realTests.map((t) => (
                <li key={t}>{bundle.rules[t] ?? t.replace(/_/g, " ")}</li>
              ))}
            </ul>
          </div>
        </details>
      )}

      <details className="grownups">
        <summary>For grown-ups: what&apos;s going on</summary>
        <div className="grownups-body">
          <p>
            {who} is <code>{bundle.program}</code>, a command-line program from chapter {bundle.number} of Ken
            Youens-Clark&apos;s <cite>Tiny Python Projects</cite>. The book&apos;s rules are his pytest suite,
            unchanged. The real-life rules are mine: cases the book doesn&apos;t cover, plus property tests.
          </p>
          <p>
            Gremlins are mutation testing: each is a copy of the program with one small change. Of {g.total}{" "}
            gremlins, the book&apos;s {book} tests catch {g.book_caught}; with the {real_life} real-life tests added,{" "}
            {g.all_caught}. {g.book_missed_real_life_caught > 0 && (
              <>
                {g.book_missed_real_life_caught} get past the book&apos;s tests and are caught by real-life ones; the
                one above is the easiest to explain.
              </>
            )}
          </p>
          <p>
            Everything above this button was recorded by CI on Python {python} ({generated}), so it shows before
            anything loads. &ldquo;Run it live&rdquo; downloads CPython compiled to WebAssembly (about 13 MB) and runs
            the same program, tests and gremlins in your browser. The tests start the program with{" "}
            <code>subprocess</code>; browsers can&apos;t start processes, so a shim runs it in-process, and CI checks
            that shim against real processes byte for byte.
          </p>
          {bundle.note && <p>{bundle.note}</p>}
          {bundle.book && bundle.brains.book && (
            <p>
              The book&apos;s own version passes the book&apos;s rules but not the real-life ones.{" "}
              <button type="button" className="link" onClick={() => goLive("book")}>
                Play {bundle.brains.book}
              </button>
            </p>
          )}
        </div>
      </details>
    </div>
  );
}
