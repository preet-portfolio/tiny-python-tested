"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Editor } from "./Editor";
import { Toy } from "./toys";
import { Gremlin } from "./Gremlin";
import { gremlinName, maskRude, prank } from "@/lib/kid";
import {
  Python,
  type Bundle,
  type MutantRow,
  type MutationResult,
  type Progress,
  type Run,
  type TestResult,
} from "@/lib/py";

export type BrainId = "book" | "real" | "yours";
export type RunFn = (args: string, opts?: { stdin?: string; brain?: BrainId }) => Promise<Run>;

const store = {
  get(key: string): string | null {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key: string, value: string) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      /* drafts just aren't kept */
    }
  },
};

const brainFile = (b: BrainId) => `.brain_${b}.py`;

export function Playground({ bundle, brainRequest }: { bundle: Bundle; brainRequest?: { brain: BrainId; n: number } }) {
  const who = bundle.character.name;
  const draftKey = `tptl:${bundle.id}:code`;
  const brains = useMemo(() => {
    const list: { id: BrainId; label: string; blurb: string }[] = [];
    if (bundle.book && bundle.brains.book)
      list.push({ id: "book", label: bundle.brains.book, blurb: bundle.brain_blurbs.book ?? "" });
    list.push({ id: "real", label: bundle.brains.real, blurb: bundle.brain_blurbs.real });
    list.push({ id: "yours", label: `Your ${who.replace(/^The /, "")}`, blurb: "Built by you, in real Python." });
    return list;
  }, [bundle, who]);

  const [brain, setBrain] = useState<BrainId>("real");
  const [yours, setYours] = useState(bundle.starter);
  const [ready, setReady] = useState(false);
  const [stage, setStage] = useState("Waking up");
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState<string | null>(null);
  const [results, setResults] = useState<{ brain: BrainId; res: TestResult } | null>(null);
  const [gremlins, setGremlins] = useState<{ brain: BrainId; book?: MutationResult; all?: MutationResult } | null>(null);
  const [gProgress, setGProgress] = useState<{ i: number; n: number; round: string } | null>(null);
  const py = useRef<Python | null>(null);
  const roundRef = useRef("");

  const code = (b: BrainId) => (b === "book" ? (bundle.book ?? "") : b === "real" ? bundle.reference : yours);

  const boot = useCallback(async () => {
    py.current?.terminate();
    const p = new Python();
    py.current = p;
    p.onProgress = (msg: Progress) => {
      if (msg.stage === "mutant" && msg.n) setGProgress({ i: msg.i ?? 0, n: msg.n, round: roundRef.current });
      else setStage(msg.stage);
    };
    setReady(false);
    setFailed(null);
    const stale = () => py.current !== p;
    try {
      await p.call<{ python: string }>("init");
      if (stale()) return;
      const saved = store.get(draftKey) ?? bundle.starter;
      setYours(saved);
      await p.call("load", { bundle, code: bundle.reference });
      if (bundle.book) await p.call("write", { name: brainFile("book"), text: bundle.book });
      await p.call("write", { name: brainFile("real"), text: bundle.reference });
      await p.call("write", { name: brainFile("yours"), text: saved });
      if (stale()) return;
      setReady(true);
    } catch (e) {
      if (!stale()) setFailed((e as Error).message);
    }
  }, [bundle, draftKey]);

  useEffect(() => {
    boot();
    return () => {
      py.current?.terminate();
      py.current = null;
    };
  }, [boot]);

  const run: RunFn = useCallback(
    async (args, opts) => {
      const p = py.current;
      if (!p) throw new Error("Python isn't ready yet.");
      const raw = await p.call<Run>("run", { args, stdin: opts?.stdin, prog: brainFile(opts?.brain ?? brain) });
      const result = { ...raw, stdout: maskRude(raw.stdout) };
      // Lighthouse and the tester brief read this: time from navigation to the toy's first answer.
      if (performance.getEntriesByName("tptl:first-answer").length === 0) performance.mark("tptl:first-answer");
      return result;
    },
    [brain],
  );

  const allFiles = useMemo(() => [...bundle.upstream_tests, ...bundle.scenario_tests], [bundle]);

  const checkRules = async () => {
    const p = py.current;
    if (!p) return;
    setBusy(true);
    try {
      await p.call("write", { name: bundle.program, text: code(brain) });
      setResults({ brain, res: await p.call<TestResult>("test", { files: allFiles }) });
    } catch (e) {
      setFailed((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const releaseGremlins = async () => {
    const p = py.current;
    if (!p) return;
    setBusy(true);
    setGremlins({ brain });
    try {
      await p.call("write", { name: bundle.program, text: code(brain) });
      const res = await p.call<TestResult>("test", { files: allFiles });
      setResults({ brain, res });
      const bookGreen = res.tests.filter((t) => bundle.upstream_tests.includes(t.file)).every((t) => t.outcome === "passed");
      const allGreen = res.failed === 0;
      if (!bookGreen) return;
      roundRef.current = "the book's rules";
      const book = await p.call<MutationResult>("mutate", { files: bundle.upstream_tests, limit: 60 });
      setGremlins({ brain, book });
      if (allGreen) {
        roundRef.current = "all the rules";
        setGProgress("total" in book ? { i: 0, n: book.total, round: roundRef.current } : null);
        const all = await p.call<MutationResult>("mutate", { files: allFiles, limit: 60 });
        setGremlins({ brain, book, all });
      }
    } catch (e) {
      setFailed((e as Error).message);
    } finally {
      setGProgress(null);
      setBusy(false);
    }
  };

  const tryYours = async (text: string) => {
    setYours(text);
    store.set(draftKey, text);
    await py.current?.call("write", { name: brainFile("yours"), text });
    setBrain("yours");
    setResults(null);
    setGremlins(null);
  };

  const pick = (b: BrainId) => {
    setBrain(b);
    setResults(null);
    setGremlins(null);
  };

  // The grown-ups section (outside this component) can ask to play the book's version.
  useEffect(() => {
    if (brainRequest) pick(brainRequest.brain);
  }, [brainRequest]);

  const current = brains.find((b) => b.id === brain)!;
  const shownResults = results?.brain === brain ? results.res : null;

  return (
    <div className="play">
      <section className="toy-card" aria-label="Play">
        {failed && (
          <p className="oops" role="alert">
            {failed}{" "}
            <button type="button" className="link" onClick={boot}>
              Try again
            </button>
          </p>
        )}
        {brain !== "real" && (
          <p className="playing-as">
            You&apos;re playing {current.label}.{" "}
            <button type="button" className="link" onClick={() => pick("real")}>
              Back to {brains.find((b) => b.id === "real")!.label}
            </button>
          </p>
        )}
        {!ready && !failed ? (
          <div className="waking">
            <span className="waking-emoji" aria-hidden="true">
              {bundle.character.emoji}
            </span>
            <p>
              {stage === "Waking up" ? `${who} is waking up…` : `${stage}…`}
              <br />
              <small>A real Python is starting in your browser. This takes a few seconds the first time.</small>
            </p>
          </div>
        ) : (
          ready && <Toy bundle={bundle} run={run} brain={brain} brainLabel={brain === "real" ? who : current.label} hasBook={false} />
        )}
      </section>

      <details className="peek">
        <summary>
          Peek inside <span>(every rule, every gremlin, and {who}&apos;s brain)</span>
        </summary>
      <RuleBoard
        bundle={bundle}
        label={brain === "real" ? who : current.label}
        results={shownResults}
        busy={busy || !ready}
        onCheck={checkRules}
      />

      <GremlinPit
        label={brain === "real" ? who : current.label}
        state={gremlins?.brain === brain ? gremlins : null}
        results={shownResults}
        progress={gProgress}
        busy={busy || !ready}
        onRelease={releaseGremlins}
        rules={bundle.rules}
        bookRuleCount={bundle.upstream_tests.length}
      />

      <h2 className="peek-h">{who}&apos;s brain <span>(real Python: change it and see)</span></h2>
        <BrainEditor
          start={code(brain === "yours" ? "yours" : brain)}
          program={bundle.program}
          onTry={tryYours}
          onReset={() => tryYours(bundle.starter)}
        />
      </details>

    </div>
  );
}

function RuleBoard({
  bundle,
  label,
  results,
  busy,
  onCheck,
}: {
  bundle: Bundle;
  label: string;
  results: TestResult | null;
  busy: boolean;
  onCheck: () => void;
}) {
  const rows = (files: string[]) =>
    results
      ? results.tests.filter((t) => files.includes(t.file))
      : null;
  const book = rows(bundle.upstream_tests);
  const world = rows(bundle.scenario_tests);
  const names = (files: string[], fallback: TestResult["tests"] | null) =>
    fallback?.map((t) => t.name) ??
    Object.keys(bundle.rules).filter((n) =>
      files.some((f) => (bundle.files[f] ?? "").includes(`def ${n}(`)),
    );
  const outcome = (list: TestResult["tests"] | null, n: string) => list?.find((t) => t.name === n)?.outcome;
  const score = (list: TestResult["tests"] | null) =>
    list ? `${list.filter((t) => t.outcome === "passed").length} of ${list.length}` : null;

  const column = (title: string, sub: string, files: string[], list: TestResult["tests"] | null) => (
    <div className="rule-col">
      <h3>
        {title} {score(list) && <span className="rule-score">{score(list)}</span>}
      </h3>
      <p className="rule-sub">{sub}</p>
      <ul className="rules">
        {names(files, list).map((n) => {
          const o = outcome(list, n);
          return (
            <li key={n} className={`rule ${o ?? "unknown"}`}>
              <span className="stamp" aria-hidden="true">
                {o === "passed" ? "✔" : o ? "✘" : "?"}
              </span>
              <span className="rule-text">{bundle.rules[n] ?? n.replace(/_/g, " ")}</span>
              <span className="sr-only">{o === "passed" ? "follows this rule" : o ? "breaks this rule" : "not checked yet"}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );

  return (
    <section className="rule-board" aria-labelledby="rules-h">
      <div className="section-head">
        <h2 id="rules-h">The rules</h2>
        <button type="button" className="big-btn" onClick={onCheck} disabled={busy}>
          {busy ? "Checking…" : `Check ${label}`}
        </button>
      </div>
      <p className="section-lede">
        Every toy here comes with a list of rules. The rules don&apos;t care how the toy works inside. They only
        check what it does.
      </p>
      <div className="rule-cols">
        {column("The book's rules", "Written by the book's author.", bundle.upstream_tests, book)}
        {column(
          bundle.world_label === "Real world" || !bundle.world_label ? "Real-life rules" : bundle.world_label === "Unit and real world" ? "Extra rules" : bundle.world_label,
          "Added by me, for things that happen in real life.",
          bundle.scenario_tests,
          world,
        )}
      </div>
    </section>
  );
}

function GremlinPit({
  label,
  state,
  results,
  progress,
  busy,
  onRelease,
  rules,
}: {
  label: string;
  state: { book?: MutationResult; all?: MutationResult } | null;
  results: TestResult | null;
  progress: { i: number; n: number; round: string } | null;
  busy: boolean;
  onRelease: () => void;
  rules: Record<string, string>;
  bookRuleCount: number;
}) {
  const [picked, setPicked] = useState<number | null>(null);
  const ok = (r?: MutationResult) => (r && "mutants" in r ? r : null);
  const book = ok(state?.book);
  const all = ok(state?.all);
  const shown = all ?? book;
  const brokeRules = results && results.failed > 0;
  const m: MutantRow | null = shown && picked != null ? shown.mutants[picked] : null;

  return (
    <section className="pit" aria-labelledby="pit-h">
      <div className="section-head">
        <h2 id="pit-h">Gremlin attack</h2>
        <button type="button" className="big-btn gremlin-btn" onClick={onRelease} disabled={busy}>
          {progress ? "Gremlins at work…" : "Let the gremlins in"}
        </button>
      </div>
      <p className="section-lede">
        Gremlins sneak into {label}&apos;s brain and change one tiny thing each. If a rule notices, the gremlin goes
        to jail. If no rule notices, it escapes, and the rules have a blind spot.
      </p>

      {progress && (
        <div className="march" role="status">
          <Gremlin className="march-g" mood="sneaky" />
          <p>
            Gremlin {progress.i + 1} of {progress.n} is trying to sneak past {progress.round}…
          </p>
          <span className="march-bar" aria-hidden="true">
            <span style={{ width: `${((progress.i + 1) / progress.n) * 100}%` }} />
          </span>
        </div>
      )}

      {state && !progress && !book && brokeRules && (
        <p className="pit-note">
          {label} breaks some of the book&apos;s rules, so every gremlin would get caught anyway. Gremlins only
          visit toys that follow the rules.
        </p>
      )}

      {book && (
        <div className="tally">
          <div className="tally-row">
            <span className="tally-label">With only the book&apos;s rules</span>
            <span className="tally-num">
              <strong>{book.killed}</strong> of {book.total} caught
            </span>
          </div>
          {all ? (
            <div className="tally-row">
              <span className="tally-label">With the real-life rules too</span>
              <span className="tally-num">
                <strong>{all.killed}</strong> of {all.total} caught
              </span>
            </div>
          ) : (
            !progress &&
            results &&
            results.failed > 0 && (
              <p className="pit-note">{label} breaks some real-life rules, so only the book&apos;s rules went up against the gremlins.</p>
            )
          )}
        </div>
      )}

      {shown && (
        <>
          <div className="jail-yard">
            <div>
              <h3>Caught</h3>
              <ul className="gremlins">
                {shown.mutants.filter((g) => g.killed).map((g) => (
                  <li key={g.id}>
                    <button type="button" className={`g-btn${picked === g.id ? " is-picked" : ""}`} onClick={() => setPicked(g.id)} aria-label={`${gremlinName(g.id)}, caught`}>
                      <Gremlin mood="caught" />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Escaped</h3>
              {shown.mutants.some((g) => !g.killed) ? (
                <ul className="gremlins">
                  {shown.mutants.filter((g) => !g.killed).map((g) => (
                    <li key={g.id}>
                      <button type="button" className={`g-btn${picked === g.id ? " is-picked" : ""}`} onClick={() => setPicked(g.id)} aria-label={`${gremlinName(g.id)}, escaped`}>
                        <Gremlin mood="free" />
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="pit-note">None! Every gremlin got caught.</p>
              )}
            </div>
          </div>
          <div className="g-card" aria-live="polite">
            {m ? (
              <>
                <p className="g-title">
                  <strong>{gremlinName(m.id)}</strong> {prank(m)} on line {m.line}.
                </p>
                <p className="g-code">
                  <code className="was">{m.before}</code> <span aria-hidden="true">→</span> <code className="now">{m.after}</code>
                </p>
                <p>
                  {m.killed
                    ? `Caught by: ${m.killed_by.map((t) => rules[t] ?? (t.startsWith("(") ? "the whole check falling over" : t)).join("; ")}.`
                    : "No rule noticed. Is this a blind spot, or a change that doesn't matter? You decide."}
                </p>
              </>
            ) : (
              <p>Tap a gremlin to see what it did.</p>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function BrainEditor({
  start,
  program,
  onTry,
  onReset,
}: {
  start: string;
  program: string;
  onTry: (text: string) => void;
  onReset: () => void;
}) {
  const [text, setText] = useState(start);
  useEffect(() => setText(start), [start]);
  return (
    <div className="brain-editor">
      <p>
        This is the actual program, <code>{program}</code>. Change it, then press the button to play with your
        version and check it against the rules.
      </p>
      <div className="editor-box">
        <Editor value={text} onChange={setText} onRun={() => onTry(text)} label={`Editor for ${program}`} />
      </div>
      <div className="row-btns">
        <button type="button" className="big-btn" onClick={() => onTry(text)}>
          Play with my version
        </button>
        <button type="button" className="soft-btn" onClick={onReset}>
          Start from a blank-ish brain
        </button>
      </div>
    </div>
  );
}
