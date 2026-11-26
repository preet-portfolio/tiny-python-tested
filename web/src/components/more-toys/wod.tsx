"use client";

import { useEffect, useState } from "react";
import { explain } from "@/lib/kid";
import type { Run } from "@/lib/py";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./wod.module.css";

/* ---------------- Coach Boing (workout of the day) ---------------- */

type ListId = "coach" | "silly" | "mine";
const ICONS = ["🤸", "🏃", "🦵", "💪", "🧘", "🙆", "🐸", "🦩", "🌀"];
const MY_LIST = "exercise,reps\nFrog jumps,5-10\nFlamingo stands,10-20\nSilly walks,8-12\nStar jumps,50-20\nFrog jumps,5-10\n";

function parse(r: Run | null): [string, string][] {
  if (r?.status !== 0) return [];
  return r.stdout
    .trim()
    .split("\n")
    .slice(2)
    .map((line) => {
      const m = line.match(/^(.*\S)\s+(\d+)$/);
      return m ? [m[1], m[2]] : ["", ""];
    })
    .filter(([n]) => n) as [string, string][];
}

export default function Wod({ bundle, run, brain, hasBook }: ToyProps) {
  const [num, setNum] = useState(4);
  const [easy, setEasy] = useState(false);
  const [seed, setSeed] = useState(1);
  const [list, setList] = useState<ListId>("coach");
  const [mineText, setMineText] = useState(MY_LIST);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);

  const plan = (o: Partial<{ num: number; easy: boolean; seed: number; list: ListId }> = {}) => {
    const n = o.num ?? num;
    const e = o.easy ?? easy;
    const s = o.seed ?? seed;
    const l = o.list ?? list;
    const file = l === "silly" ? " -f inputs/silly-exercises.csv" : l === "mine" ? " -f -" : "";
    go(`-n ${n} -s ${s}${e ? " -e" : ""}${file}`, l === "mine" ? mineText : undefined);
  };
  useEffect(() => {
    go("-n 4 -s 1");
  }, [go]);

  const rows = parse(mine);
  const theirs = parse(other);

  return (
    <div className="toy">
      <div className="toy-form">
        <p className="chips-label">Which list of exercises?</p>
        <Chips
          items={[["🦘", "Coach's list"], ["🤪", "Silly list"], ["✏️", "My own list"]]}
          onPick={(v) => {
            const l: ListId = v.startsWith("Coach") ? "coach" : v.startsWith("Silly") ? "silly" : "mine";
            setList(l);
            plan({ list: l });
          }}
          label="Exercise lists"
        />
        {list === "mine" && (
          <>
            <label htmlFor="wod-list">Your list: one exercise per line, then the fewest and most reps</label>
            <textarea id="wod-list" rows={5} value={mineText} onChange={(e) => setMineText(e.target.value)} />
          </>
        )}
        <div className="field-row">
          <label htmlFor="wod-num" className="inline-label">
            How many exercises: {num}
          </label>
          <input
            id="wod-num"
            className={styles.range}
            type="range"
            min={1}
            max={12}
            value={num}
            onChange={(e) => setNum(parseInt(e.target.value, 10))}
          />
          <label className={styles.toggle}>
            <input type="checkbox" checked={easy} onChange={(e) => setEasy(e.target.checked)} />
            Easy day
          </label>
        </div>
        <div className="field-row">
          <label htmlFor="wod-seed" className="inline-label">
            Lucky number
          </label>
          <input id="wod-seed" className="seed" type="number" value={seed} onChange={(e) => setSeed(parseInt(e.target.value, 10) || 0)} />
          <button
            type="button"
            className="soft-btn"
            onClick={() => {
              const s = Math.floor(Math.random() * 1000);
              setSeed(s);
              plan({ seed: s });
            }}
          >
            <span aria-hidden="true">🎲 </span>Roll
          </button>
          <button type="button" className="big-btn" disabled={busy} onClick={() => plan()}>
            Boing! Plan my workout
          </button>
        </div>
      </div>
      <Oops run={mine} />
      {rows.length > 0 && (
        <div className={styles.cards} aria-live="polite">
          {rows.map(([name, reps], i) => (
            <div key={`${name}-${i}`} className={styles.card} style={{ animationDelay: `${i * 70}ms` }}>
              <span className={styles.icon} aria-hidden="true">
                {ICONS[i % ICONS.length]}
              </span>
              <strong>{reps}</strong>
              <span>{name}</span>
            </div>
          ))}
        </div>
      )}
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would say:{" "}
          <q>{other.status === 0 ? theirs.map(([n, r]) => `${r} ${n}`).join(", ") : explain(other)}</q>
        </p>
      )}
    </div>
  );
}
