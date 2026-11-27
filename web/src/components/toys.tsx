"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { explain, quote } from "@/lib/kid";
import type { Bundle, Run } from "@/lib/py";
import type { BrainId, RunFn } from "./Playground";
import { MORE_TOYS } from "./more-toys";

export type ToyProps = { bundle: Bundle; run: RunFn; brain: BrainId; brainLabel: string; hasBook: boolean };

export function Toy(props: ToyProps) {
  switch (props.bundle.toy) {
    case "crowsnest":
      return <Lookout {...props} />;
    case "bottles":
      return <Choir {...props} />;
    case "ransom":
      return <Ransom {...props} />;
    case "wc":
      return <Owl {...props} />;
    case "tictactoe":
      return <Referee {...props} />;
    default: {
      const More = MORE_TOYS[props.bundle.toy];
      return More ? <More {...props} /> : null;
    }
  }
}

/** Run with the chosen brain, and with the other one when it might disagree. */
export function useCompare(run: RunFn, brain: BrainId, hasBook: boolean) {
  const [mine, setMine] = useState<Run | null>(null);
  const [other, setOther] = useState<Run | null>(null);
  const [busy, setBusy] = useState(false);
  const seq = useRef(0);
  const go = useCallback(
    async (args: string, stdin?: string) => {
      const n = ++seq.current;
      setBusy(true);
      try {
        const a = await run(args, { stdin, brain });
        const rival: BrainId | null = brain === "book" ? "real" : hasBook ? "book" : null;
        const b = rival ? await run(args, { stdin, brain: rival }) : null;
        if (n !== seq.current) return;
        setMine(a);
        setOther(b);
      } catch {
        // Python restarted under us (a reload or "Try again"); the next press works.
      } finally {
        if (n === seq.current) setBusy(false);
      }
    },
    [run, brain, hasBook],
  );
  return { mine, other, busy, go };
}

export const differs = (a: Run | null, b: Run | null) => !!a && !!b && (a.stdout !== b.stdout || a.status !== b.status);
export const rivalName = (bundle: Bundle, brain: BrainId) =>
  brain === "book" ? bundle.brains.real : (bundle.brains.book ?? bundle.brains.real);

export function Oops({ run }: { run: Run | null }) {
  const why = run ? explain(run) : null;
  return why ? (
    <p className="toy-oops" role="status">
      <span aria-hidden="true">⚠️ </span>
      {why}
    </p>
  ) : null;
}

export function Chips({ items, onPick, label }: { items: [string, string][]; onPick: (v: string) => void; label: string }) {
  return (
    <div className="chips" role="group" aria-label={label}>
      {items.map(([icon, v]) => (
        <button key={v} type="button" className="chip" onClick={() => onPick(v)}>
          {icon && <span aria-hidden="true">{icon} </span>}
          {v}
        </button>
      ))}
    </div>
  );
}

/* ---------------- Polly the lookout (crowsnest) ---------------- */

function Lookout({ bundle, run, brain, hasBook }: ToyProps) {
  const [word, setWord] = useState("octopus");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const spot = (w: string) => {
    setWord(w);
    if (w.trim()) go(quote(w.trim()));
  };
  useEffect(() => {
    go(quote("octopus"));
  }, [go]);
  const said = mine?.status === 0 ? mine.stdout.trim() : null;

  return (
    <div className="toy toy-lookout">
      <div className="mast" aria-hidden="true">
        <span className="mast-bird">{bundle.character.emoji}</span>
        <span className="mast-sea">🌊🌊🌊</span>
      </div>
      <div className="toy-main">
        <p className="bubble" aria-live="polite">
          {busy && !said ? "…" : said ?? "Squawk?"}
        </p>
        <Oops run={mine} />
        {differs(mine, other) && other?.status === 0 && (
          <p className="rival">
            {rivalName(bundle, brain)} would shout: <q>{other.stdout.trim()}</q>
          </p>
        )}
        <form
          className="toy-form"
          onSubmit={(e) => {
            e.preventDefault();
            spot(word);
          }}
        >
          <label htmlFor="spot">What does Polly spot?</label>
          <div className="field-row">
            <input id="spot" value={word} onChange={(e) => setWord(e.target.value)} autoComplete="off" />
            <button type="submit" className="big-btn" disabled={busy}>
              Look!
            </button>
          </div>
        </form>
        <Chips items={bundle.examples ?? []} onPick={spot} label="Things to spot" />
      </div>
    </div>
  );
}

/* ---------------- The bottle choir (bottles) ---------------- */

function Choir({ run, brain }: ToyProps) {
  const [num, setNum] = useState("3");
  const { mine, busy, go } = useCompare(run, brain, false);
  const sing = (n: string) => {
    setNum(n);
    // The book's song is about beer; the choir here sings about lemonade.
    go(`-n ${quote(n.trim() || "''")} --drink lemonade`);
  };
  useEffect(() => {
    go("-n 3 --drink lemonade");
  }, [go]);
  const verses = mine?.status === 0 ? mine.stdout.trim().split("\n\n") : [];
  const count = Math.max(0, Math.min(40, parseInt(num, 10) || 0));

  return (
    <div className="toy toy-choir">
      <div className="shelf" aria-hidden="true">
        {Array.from({ length: count }, (_, i) => (
          <span key={i} className="bottle" style={{ animationDelay: `${i * 40}ms` }}>
            🍾
          </span>
        ))}
        {count === 0 && <span className="shelf-empty">empty wall</span>}
      </div>
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          sing(num);
        }}
      >
        <label htmlFor="num">How many bottles on the wall?</label>
        <div className="field-row">
          <input id="num" value={num} onChange={(e) => setNum(e.target.value)} inputMode="numeric" autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Sing!
          </button>
        </div>
      </form>
      <Chips
        items={[["", "1"], ["", "10"], ["😬", "0"], ["🤔", "2.5"], ["🍌", "banana"], ["😱", "99"]]}
        onPick={sing}
        label="Try a number"
      />
      <Oops run={mine} />
      {verses.length > 0 && (
        <div className="songbook" aria-live="polite">
          <p className="songbook-count">
            {verses.length} {verses.length === 1 ? "verse" : "verses"}
          </p>
          <ol>
            {verses.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

/* ---------------- Whiskers' ransom notes (ransom) ---------------- */

const FONTS = ["var(--font-display)", "Georgia, serif", "var(--font-body)", "'Courier New', monospace", "Impact, sans-serif"];
const PAPERS = ["#fff7d6", "#ffffff", "#d8f0ff", "#ffe0e6", "#e2f7d8", "#1f2a44"];

function letterStyle(ch: string, i: number): React.CSSProperties {
  const h = (ch.codePointAt(0) ?? 0) * 31 + i * 17;
  const paper = PAPERS[h % PAPERS.length];
  return {
    fontFamily: FONTS[(h >> 2) % FONTS.length],
    background: paper,
    color: paper === "#1f2a44" ? "#fff" : "#1f2a44",
    transform: `rotate(${((h % 9) - 4) * 1.5}deg) translateY(${(h % 5) - 2}px)`,
  };
}

function Ransom({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("Give me treats or else");
  const [seed, setSeed] = useState(7);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const write = (t = text, s = seed) => go(`-s ${s} ${quote(t || "''")}`);
  useEffect(() => {
    go(`-s 7 ${quote("Give me treats or else")}`);
  }, [go]);
  const note = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;
  const len = (s: string) => [...s].length;

  return (
    <div className="toy toy-ransom">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          write();
        }}
      >
        <label htmlFor="demand">Whiskers demands…</label>
        <textarea id="demand" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="field-row">
          <label htmlFor="seed" className="inline-label">
            Lucky number
          </label>
          <input
            id="seed"
            className="seed"
            type="number"
            value={seed}
            onChange={(e) => setSeed(parseInt(e.target.value, 10) || 0)}
          />
          <button
            type="button"
            className="soft-btn"
            onClick={() => {
              const s = Math.floor(Math.random() * 1000);
              setSeed(s);
              write(text, s);
            }}
          >
            <span aria-hidden="true">🎲 </span>Roll
          </button>
          <button type="submit" className="big-btn" disabled={busy}>
            Cut it out!
          </button>
        </div>
      </form>
      <Chips
        items={[["🇩🇪", "Straße"], ["🇹🇷", "İstanbul"], ["🐟", "MORE TUNA"]]}
        onPick={(t) => {
          setText(t);
          write(t);
        }}
        label="Tricky words"
      />
      <Oops run={mine} />
      {note != null && (
        <div className="note-paper" aria-label={`Ransom note: ${note}`} aria-live="polite">
          {[...note].map((ch, i) =>
            ch === " " ? (
              <span key={i} className="gap" />
            ) : ch === "\n" ? (
              <br key={i} />
            ) : (
              <span key={i} className="cut" style={letterStyle(ch, i)}>
                {ch}
              </span>
            ),
          )}
        </div>
      )}
      {note != null && len(note) !== len(text) && (
        <p className="rival">
          Uh-oh: you wrote {len(text)} letters, but the note has {len(note)}. A letter turned into two!
        </p>
      )}
      {differs(mine, other) && other?.status === 0 && len(other.stdout.replace(/\n$/, "")) !== len(note ?? "") && (
        <p className="rival">
          {rivalName(bundle, brain)} would make a note with {len(other.stdout.replace(/\n$/, ""))} letters.
        </p>
      )}
    </div>
  );
}

/* ---------------- Professor Hoot counts (wc) ---------------- */

const SAMPLES: [string, string, string][] = [
  ["☕", "café crème", "café crème"],
  ["✏️", "no Enter at the end", "one line\ntwo lines"],
  ["🪟", "Windows text", "line one\r\nline two\r\n"],
  ["😀", "emoji", "hello 👋🌍\n"],
];

function Owl({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("The owl\nsaw a mouse.\n");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const count = (t = text) => go("", t);
  useEffect(() => {
    go("", "The owl\nsaw a mouse.\n");
  }, [go]);
  const nums = (r: Run | null) =>
    r?.status === 0 ? r.stdout.trim().split(/\s+/).slice(0, 3).map(Number) : null;
  const n = nums(mine);
  const o = nums(other);
  const labels = ["lines", "words", "bytes"];

  return (
    <div className="toy toy-owl">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          count();
        }}
      >
        <label htmlFor="words">Give the professor something to count</label>
        <textarea id="words" rows={4} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="field-row">
          <button type="submit" className="big-btn" disabled={busy}>
            Count it!
          </button>
        </div>
      </form>
      <Chips
        items={SAMPLES.map(([i, label]) => [i, label])}
        onPick={(label) => {
          const t = SAMPLES.find((s) => s[1] === label)![2];
          setText(t);
          count(t);
        }}
        label="Tricky text"
      />
      <Oops run={mine} />
      {n && (
        <div className="counters" aria-live="polite">
          {n.map((v, i) => (
            <div key={labels[i]} className="counter">
              <strong>{v}</strong>
              <span>{labels[i]}</span>
              {o && o[i] !== v && (
                <small>
                  {rivalName(bundle, brain)}: {o[i]}
                </small>
              )}
            </div>
          ))}
          <div className="counter counter-quiet">
            <strong>{[...text].length}</strong>
            <span>letters you can see</span>
          </div>
        </div>
      )}
      {n && n[2] !== [...text].length && (
        <p className="hint">
          Bytes and letters don&apos;t match? Some letters, like é or 👋, take more than one byte to store.
        </p>
      )}
    </div>
  );
}

/* ---------------- Ref Robo (tictactoe) ---------------- */

const EMPTY = ".........";
const WEIRD: [string, string, string][] = [
  ["🤯", "two winners", "XXXOOO..."],
  ["🙈", "X cheated", "XXXXX...."],
  ["🔡", "lower-case", "xxx......"],
  ["🧩", "nearly done", "XOXOXO.O."],
];

function parseBoard(out: string): string | null {
  const rows = out.split("\n").filter((l) => l.startsWith("|"));
  if (rows.length !== 3) return null;
  return rows
    .flatMap((r) => r.split("|").slice(1, 4).map((c) => c.trim()))
    .map((c) => (/^\d$/.test(c) ? "." : c))
    .join("");
}

function Referee({ bundle, run, brain, hasBook }: ToyProps) {
  const [board, setBoard] = useState(EMPTY);
  const [turn, setTurn] = useState<"X" | "O">("X");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const [verdict, setVerdict] = useState("X goes first. Tap a square.");

  useEffect(() => {
    if (!mine) return;
    if (mine.status === 0) {
      const b = parseBoard(mine.stdout);
      if (b) setBoard(b);
      setVerdict(mine.stdout.trim().split("\n").pop() ?? "");
    }
  }, [mine]);

  const play = (cell: number) => {
    if (busy) return;
    go(`-b ${board} -p ${turn} -c ${cell + 1}`).then(() => undefined);
    setTurn((t) => (t === "X" ? "O" : "X"));
  };
  const sneak = (b: string) => {
    setBoard(b);
    go(`-b ${b}`);
  };
  const reset = () => {
    setBoard(EMPTY);
    setTurn("X");
    setVerdict("X goes first. Tap a square.");
    go(`-b ${EMPTY}`);
  };
  const okVerdict = mine?.status === 0;
  const over = okVerdict && /won/.test(verdict);

  return (
    <div className="toy toy-ref">
      <div className="board-wrap">
        <div className="board" role="grid" aria-label="Noughts and crosses board">
          {[0, 1, 2].map((r) => (
            <div role="row" key={r} className="board-row">
              {[0, 1, 2].map((c) => {
                const i = r * 3 + c;
                const v = board[i];
                return (
                  <button
                    key={i}
                    role="gridcell"
                    type="button"
                    className={`cell cell-${v === "." ? "empty" : v.toUpperCase()}`}
                    onClick={() => play(i)}
                    aria-label={`Square ${i + 1}: ${v === "." ? "empty" : v}`}
                  >
                    {v === "." ? "" : v}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
        <div className="ref-side">
          <p className="bubble" aria-live="polite">
            {okVerdict || !mine ? verdict : explain(mine)}
          </p>
          {!over && <p className="turn">Next up: {turn}</p>}
          {differs(mine, other) && (
            <p className="rival">
              {rivalName(bundle, brain)} would say:{" "}
              <q>{other?.status === 0 ? other.stdout.trim().split("\n").pop() : explain(other!)}</q>
            </p>
          )}
          <button type="button" className="soft-btn" onClick={reset}>
            New game
          </button>
        </div>
      </div>
      <p className="chips-label">Try to fool the ref with a board that could never happen:</p>
      <Chips items={WEIRD.map(([i, l]) => [i, l])} onPick={(l) => sneak(WEIRD.find((w) => w[1] === l)![2])} label="Weird boards" />
    </div>
  );
}
