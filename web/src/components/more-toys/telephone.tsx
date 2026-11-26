"use client";

import { useEffect, useState } from "react";
import type { Run } from "@/lib/py";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./telephone.module.css";

/* ---------------- Mumbles passes it on (telephone) ---------------- */

/** What Mumbles heard, from 'You said: "..."\nI heard : "..."'. */
const heard = (r: Run | null) => {
  if (r?.status !== 0) return null;
  const parts = r.stdout.replace(/\n$/, "").split('\nI heard : "');
  return parts.length === 2 ? parts[1].slice(0, -1) : null;
};

function Marked({ said, got }: { said: string; got: string }) {
  const a = [...said];
  return (
    <>
      {[...got].map((c, i) =>
        c === a[i] ? (
          <span key={i}>{c}</span>
        ) : c === "\n" || a[i] === "\n" ? (
          <mark key={i} className={styles.broken} title="A line break got muddled">
            {c === "\n" ? "↵" : c}
          </mark>
        ) : (
          <mark key={i} className={styles.oops}>
            {c}
          </mark>
        ),
      )}
    </>
  );
}

const TRICKS: [string, string, string, number][] = [
  ["🤏", "A tiny word", "Hi!", 10],
  ["📋", "A three-line list", "eggs\nmilk\nbread", 60],
  ["🤫", "No noise at all", "Pass it on", 0],
];

export default function Telephone({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("Meet me by the big oak tree");
  const [noise, setNoise] = useState(20);
  const [seed, setSeed] = useState(1);
  const [said, setSaid] = useState("Meet me by the big oak tree");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const whisper = (t = text, n = noise, s = seed) => {
    setSaid(t);
    go(`-s ${s} -m ${n / 100} ${quote(t || "''")}`);
  };
  useEffect(() => {
    go(`-s 1 -m 0.2 ${quote("Meet me by the big oak tree")}`);
  }, [go]);

  const got = heard(mine);
  const theirs = heard(other);
  const changed = got == null ? 0 : [...got].filter((c, i) => c !== [...said][i]).length;

  return (
    <div className="toy">
      <div className={styles.line} aria-hidden="true">
        🧒 <span className={styles.wire} /> {bundle.character.emoji}
      </div>
      <div className={styles.cards} aria-live="polite">
        <p className={styles.card}>
          <strong>You said</strong>
          <span className={styles.msg}>{said}</span>
        </p>
        <p className={styles.card}>
          <strong>{bundle.character.name} heard</strong>
          <span className={styles.msg}>{busy && got == null ? "…" : got != null ? <Marked said={said} got={got} /> : "Huh?"}</span>
        </p>
      </div>
      {got != null && (
        <p className="hint">
          {changed === 0 ? "Heard it perfectly!" : `${changed} ${changed === 1 ? "letter" : "letters"} got muddled.`}
        </p>
      )}
      <Oops run={mine} />
      {differs(mine, other) && theirs != null && (
        <p className="rival">
          {rivalName(bundle, brain)} would hear: <q className={styles.msg}>{theirs}</q>
        </p>
      )}
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          whisper();
        }}
      >
        <label htmlFor="mumbles-text">Whisper a message</label>
        <textarea id="mumbles-text" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <label className={styles.noise}>
          Noise: <strong>{noise}%</strong>
          <input type="range" min={0} max={100} value={noise} onChange={(e) => setNoise(+e.target.value)} />
        </label>
        <div className="field-row">
          <label htmlFor="mumbles-seed" className="inline-label">
            Lucky number
          </label>
          <input id="mumbles-seed" className="seed" type="number" value={seed} onChange={(e) => setSeed(parseInt(e.target.value, 10) || 0)} />
          <button type="submit" className="big-btn" disabled={busy}>
            Whisper!
          </button>
        </div>
      </form>
      {got != null && (
        <button
          type="button"
          className="soft-btn"
          disabled={busy}
          onClick={() => {
            setText(got);
            setSeed(seed + 1);
            whisper(got, noise, seed + 1);
          }}
        >
          <span aria-hidden="true">📞 </span>Pass it on to the next friend
        </button>
      )}
      <Chips
        items={TRICKS.map(([i, l]) => [i, l])}
        onPick={(l) => {
          const [, , t, n] = TRICKS.find((x) => x[1] === l)!;
          setText(t);
          setNoise(n);
          whisper(t, n);
        }}
        label="Things to whisper"
      />
    </div>
  );
}
