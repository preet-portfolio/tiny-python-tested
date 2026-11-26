"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./gematria.module.css";

/* ---------------- Abacus Annie (gematria) ---------------- */

const numbersOf = (out: string) => out.replace(/\n$/, "").split("\n").map((l) => l.split(/\s+/).filter(Boolean));

export default function Gematria({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("listen silent");
  const [sent, setSent] = useState("listen silent");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const count = (t: string) => {
    setText(t);
    setSent(t);
    go(quote(t || "''"));
  };
  useEffect(() => {
    go(quote("listen silent"));
  }, [go]);

  const lines = mine?.status === 0 ? numbersOf(mine.stdout) : null;
  const textLines = sent.split("\n").map((l) => l.split(/\s+/).filter(Boolean));
  const all = lines?.flat() ?? [];
  const twins = new Set(all.filter((n, i) => all.indexOf(n) !== i));

  return (
    <div className="toy">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          count(text);
        }}
      >
        <label htmlFor="gem-text">Give Annie some words to count</label>
        <textarea id="gem-text" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="field-row">
          <button type="submit" className="big-btn" disabled={busy}>
            Add them up!
          </button>
        </div>
      </form>
      <Chips items={bundle.examples ?? []} onPick={count} label="Words to try" />
      <Oops run={mine} />
      {lines && (
        <div className={styles.lines} aria-live="polite">
          {lines.map((nums, li) => {
            // Each number belongs to a word, unless Annie skipped a bit that wasn't a word.
            const words = textLines[li] ?? [];
            const sameCount = words.length === nums.length;
            return (
              <div key={li} className={styles.line}>
                {nums.map((n, i) => (
                  <div key={i} className={`${styles.card} ${twins.has(n) ? styles.twin : ""}`}>
                    <strong>{n}</strong>
                    {sameCount && <span>{words[i]}</span>}
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}
      {twins.size > 0 && (
        <p className="hint">
          <span aria-hidden="true">🤯 </span>The yellow cards have the same number, even though the words are different!
        </p>
      )}
      {differs(mine, other) && other?.status === 0 && (
        <p className="rival">
          {rivalName(bundle, brain)} would count: <q>{other.stdout.trim().replace(/\n/g, " / ")}</q>
        </p>
      )}
    </div>
  );
}
