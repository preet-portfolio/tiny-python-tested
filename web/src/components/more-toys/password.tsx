"use client";

import { useEffect, useState } from "react";
import { explain, isRude } from "@/lib/kid";
import type { Run } from "@/lib/py";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./password.module.css";

/* ---------------- Shh the secret-password snail (password) ---------------- */

const COLORS = ["#ffe08a", "#bfe8ff", "#ffd1dc", "#c9f2c7", "#e3d4ff", "#ffd8b0"];
const MY_WORDS = "moon pickle pony sock\nrocket waffle tiger cloud\n";

const lines = (r: Run | null) => (r?.status === 0 ? r.stdout.trim().split("\n").filter(Boolean) : []);
/** "MoonPicklePony" -> ["Moon", "Pickle", "Pony"]; secret-code ones stay whole. */
const pieces = (pw: string) => (/^([A-Z][a-z]+)+$/.test(pw) ? (pw.match(/[A-Z][a-z]+/g) ?? [pw]) : [pw]);

export default function Password({ bundle, run, brain, hasBook }: ToyProps) {
  const [own, setOwn] = useState(false);
  const [words, setWords] = useState(MY_WORDS);
  const [perPw, setPerPw] = useState(4);
  const [howMany, setHowMany] = useState(3);
  const [leet, setLeet] = useState(false);
  const [seed, setSeed] = useState(1);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);

  const make = (o: Partial<{ own: boolean; seed: number }> = {}) => {
    const useOwn = o.own ?? own;
    const s = o.seed ?? seed;
    const src = useOwn ? "-" : "../inputs/words.txt";
    go(`-s ${s} -w ${perPw} -n ${howMany}${leet ? " -l" : ""} ${src}`, useOwn ? words : undefined);
  };
  useEffect(() => {
    go("-s 1 -w 4 -n 3 ../inputs/words.txt");
  }, [go]);

  const made = lines(mine);

  return (
    <div className="toy">
      <p className="chips-label">Where should Shh find words?</p>
      <Chips
        items={[["📚", "The giant dictionary"], ["✏️", "My own words"]]}
        onPick={(v) => {
          const o = v.startsWith("My");
          setOwn(o);
          make({ own: o });
        }}
        label="Word lists"
      />
      {own && (
        <div className="toy-form">
          <label htmlFor="pw-words">Your words (try just three, and ask for four per password!)</label>
          <textarea id="pw-words" rows={3} value={words} onChange={(e) => setWords(e.target.value)} />
        </div>
      )}
      <div className="field-row">
        <label htmlFor="pw-per" className="inline-label">
          Words each
        </label>
        <input id="pw-per" className={styles.small} type="number" min={0} max={8} value={perPw} onChange={(e) => setPerPw(parseInt(e.target.value, 10) || 0)} />
        <label htmlFor="pw-num" className="inline-label">
          How many
        </label>
        <input id="pw-num" className={styles.small} type="number" min={1} max={8} value={howMany} onChange={(e) => setHowMany(parseInt(e.target.value, 10) || 1)} />
        <label className={styles.toggle}>
          <input type="checkbox" checked={leet} onChange={(e) => setLeet(e.target.checked)} />
          Secret code
        </label>
      </div>
      <div className="field-row">
        <label htmlFor="pw-seed" className="inline-label">
          Lucky number
        </label>
        <input id="pw-seed" className="seed" type="number" value={seed} onChange={(e) => setSeed(parseInt(e.target.value, 10) || 0)} />
        <button
          type="button"
          className="soft-btn"
          onClick={() => {
            const s = Math.floor(Math.random() * 100000);
            setSeed(s);
            make({ seed: s });
          }}
        >
          <span aria-hidden="true">🎲 </span>Roll
        </button>
        <button type="button" className="big-btn" disabled={busy} onClick={() => make()}>
          Make passwords
        </button>
      </div>
      <Oops run={mine} />
      {made.length > 0 && (
        <ul className={styles.list} aria-live="polite">
          {made.map((pw, i) => (
            <li key={i} className={styles.pw} aria-label={pieces(pw).some(isRude) ? "a rude word, crossed out" : pw}>
              {pieces(pw).map((p, j) => (
                <span key={j} className={styles.part} style={{ background: COLORS[(i + j) % COLORS.length] }}>
                  {isRude(p) ? "🙊" : p}
                </span>
              ))}
            </li>
          ))}
        </ul>
      )}
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would say: <q>{other.status === 0 ? lines(other).join(", ") : explain(other)}</q>
        </p>
      )}
      <p className="hint">
        These are for fun and practice. For a real account, ask a grown-up to help you use a password manager.
      </p>
    </div>
  );
}
