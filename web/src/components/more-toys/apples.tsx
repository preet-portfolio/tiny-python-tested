"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./apples.module.css";

/* ---------------- Melody the singing frog (apples) ---------------- */

const VOWELS = ["a", "e", "i", "o", "u"];

export default function Apples({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("I like to eat apples and bananas");
  const [vowel, setVowel] = useState("o");
  const [shout, setShout] = useState(false);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const sing = (t = text, v = vowel, big = shout) => go(`-v ${big ? v.toUpperCase() : v} ${quote(t || "''")}`);
  useEffect(() => {
    go(`-v o ${quote("I like to eat apples and bananas")}`);
  }, [go]);

  const song = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;

  return (
    <div className="toy">
      <div className={styles.pond}>
        <span className={`${styles.frog} ${busy ? styles.hop : ""}`} aria-hidden="true">
          {bundle.character.emoji}
        </span>
        <p className="bubble" aria-live="polite">
          {busy && song == null ? "…" : song != null ? <>🎵 {song} 🎵</> : "Ribbit?"}
        </p>
      </div>
      <Oops run={mine} />
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would {other.status === 0 ? "sing" : "say"}:{" "}
          <q>{other.status === 0 ? other.stdout.replace(/\n$/, "") : "That's not a vowel I know!"}</q>
        </p>
      )}
      <div className={styles.vowels} role="group" aria-label="Pick Melody's vowel">
        {VOWELS.map((v) => (
          <button
            key={v}
            type="button"
            className={styles.vowel}
            aria-pressed={vowel === v}
            disabled={busy}
            onClick={() => {
              setVowel(v);
              sing(text, v);
            }}
          >
            {shout ? v.toUpperCase() : v}
          </button>
        ))}
      </div>
      <label className={styles.toggle}>
        <input
          type="checkbox"
          checked={shout}
          onChange={(e) => {
            setShout(e.target.checked);
            sing(text, vowel, e.target.checked);
          }}
        />{" "}
        Pick the vowel as a CAPITAL
      </label>
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          sing();
        }}
      >
        <label htmlFor="melody-text">What should Melody sing?</label>
        <div className="field-row">
          <input id="melody-text" value={text} onChange={(e) => setText(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Sing!
          </button>
        </div>
      </form>
      <Chips
        items={bundle.examples ?? []}
        onPick={(t) => {
          setText(t);
          sing(t);
        }}
        label="Words to sing"
      />
    </div>
  );
}
