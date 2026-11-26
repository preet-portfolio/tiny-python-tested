"use client";

import { useEffect, useState } from "react";
import type { Run } from "@/lib/py";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./abuse.module.css";

/* ---------------- Sir Bluster hurls Shakespeare (abuse) ---------------- */

const SHOWN = 12;
const lines = (r: Run | null) => (r?.status === 0 ? r.stdout.trim().split("\n") : []);
const repeats = (ls: string[]) => ls.length - new Set(ls).size;

const TRICKS: [string, string, number, number][] = [
  ["🔁", "300 insults: any repeats?", 300, 1],
  ["🤯", "40 fancy words (there are 36)", 1, 40],
  ["🙊", "Zero insults", 0, 2],
];

export default function Abuse({ bundle, run, brain, hasBook }: ToyProps) {
  const [number, setNumber] = useState(3);
  const [adjectives, setAdjectives] = useState(2);
  const [seed, setSeed] = useState(2);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const hurl = (n = number, a = adjectives, s = seed) => go(`-s ${s} -n ${n} -a ${a}`);
  useEffect(() => {
    go("-s 2 -n 3 -a 2");
  }, [go]);

  const mineLines = lines(mine);
  const otherLines = lines(other);

  return (
    <div className="toy">
      <div className={styles.stage}>
        <span className={styles.actor} aria-hidden="true">
          {bundle.character.emoji}
        </span>
        <ol className={styles.script} aria-live="polite">
          {busy && !mine && <li>…</li>}
          {mineLines.slice(0, SHOWN).map((l, i) => (
            <li key={i} className={styles.line}>
              {l}
            </li>
          ))}
        </ol>
      </div>
      {mineLines.length > SHOWN && (
        <p className="hint">
          …and {mineLines.length - SHOWN} more.{" "}
          {repeats(mineLines) ? `Sir Bluster said ${repeats(mineLines)} of them twice!` : "Not one of them said twice."}
        </p>
      )}
      <Oops run={mine} />
      {differs(mine, other) && other && (
        <p className="rival">
          {other.status !== 0
            ? `${rivalName(bundle, brain)} would ${other.stderr.includes("Traceback") ? "forget his lines and crash" : "refuse"} here.`
            : repeats(otherLines) !== repeats(mineLines)
              ? `${rivalName(bundle, brain)} would repeat himself ${repeats(otherLines)} times.`
              : `${rivalName(bundle, brain)} would say something different.`}
        </p>
      )}
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          hurl();
        }}
      >
        <div className={styles.dials}>
          <label>
            Insults: <strong>{number}</strong>
            <input type="range" min={1} max={10} value={Math.min(number, 10)} onChange={(e) => setNumber(+e.target.value)} />
          </label>
          <label>
            Fancy words in each: <strong>{adjectives}</strong>
            <input type="range" min={1} max={6} value={Math.min(adjectives, 6)} onChange={(e) => setAdjectives(+e.target.value)} />
          </label>
        </div>
        <div className="field-row">
          <label htmlFor="bluster-seed" className="inline-label">
            Lucky number
          </label>
          <input id="bluster-seed" className="seed" type="number" value={seed} onChange={(e) => setSeed(parseInt(e.target.value, 10) || 0)} />
          <button
            type="button"
            className="soft-btn"
            onClick={() => {
              const s = Math.floor(Math.random() * 1000);
              setSeed(s);
              hurl(number, adjectives, s);
            }}
          >
            <span aria-hidden="true">🎲 </span>Roll
          </button>
          <button type="submit" className="big-btn" disabled={busy}>
            Have at thee!
          </button>
        </div>
      </form>
      <Chips
        items={TRICKS.map(([i, l]) => [i, l])}
        onPick={(l) => {
          const [, , n, a] = TRICKS.find((t) => t[1] === l)!;
          setNumber(n);
          setAdjectives(a);
          hurl(n, a);
        }}
        label="Push Sir Bluster too far"
      />
      <p className="hint">These are real words from Shakespeare&apos;s plays, 400 years old. &quot;Cullionly&quot; means rascally, and a &quot;milksop&quot; is a scaredy-cat.</p>
    </div>
  );
}
