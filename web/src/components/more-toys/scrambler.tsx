"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./scrambler.module.css";

/* ---------------- Scramble the octopus (scrambler) ---------------- */

export default function Scrambler({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("Your brain is amazing at reading words");
  const [seed, setSeed] = useState(4);
  const [sent, setSent] = useState(text);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const juggle = (t = text, s = seed) => {
    setSent(t);
    go(`-s ${s} ${quote(t || "''")}`);
  };
  useEffect(() => {
    go(`-s 4 ${quote("Your brain is amazing at reading words")}`);
  }, [go]);
  const out = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;
  const before = [...sent];
  const moved = out ? [...out].filter((c, i) => c !== before[i]).length : 0;

  return (
    <div className="toy">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          juggle();
        }}
      >
        <label htmlFor="scramble-text">What should Scramble juggle?</label>
        <textarea id="scramble-text" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="field-row">
          <label htmlFor="scramble-seed" className="inline-label">
            Lucky number
          </label>
          <input
            id="scramble-seed"
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
              juggle(text, s);
            }}
          >
            <span aria-hidden="true">🎲 </span>Roll
          </button>
          <button type="submit" className="big-btn" disabled={busy}>
            Juggle!
          </button>
        </div>
      </form>
      <Chips
        items={bundle.examples ?? []}
        onPick={(t) => {
          setText(t);
          juggle(t);
        }}
        label="Things to juggle"
      />
      <Oops run={mine} />
      {out != null && (
        <>
          <div className={styles.tiles} aria-label={`Scrambled: ${out}`} aria-live="polite">
            {[...out].map((ch, i) =>
              ch === " " ? (
                <span key={i} className={styles.space} />
              ) : ch === "\n" ? (
                <br key={i} />
              ) : (
                <span key={`${i}-${ch}`} className={ch === before[i] ? styles.same : styles.moved} style={{ animationDelay: `${i * 8}ms` }}>
                  {ch}
                </span>
              ),
            )}
          </div>
          <p className="hint">
            {moved === 0 ? "Nothing moved this time. Try another lucky number!" : `${moved} letters got juggled (the blue ones). Can you still read it?`}
          </p>
        </>
      )}
      {differs(mine, other) && other?.status === 0 && (
        <p className="rival">
          {rivalName(bundle, brain)} would juggle it like this: <q>{other.stdout.trim()}</q>
        </p>
      )}
    </div>
  );
}
