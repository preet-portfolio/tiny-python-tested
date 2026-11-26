"use client";

import { useEffect, useState } from "react";
import type { Run } from "@/lib/py";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./howler.module.css";

/* ---------------- Howie the howler monkey (howler) ---------------- */

type Mode = "say" | "pipe";
const SCROLL = "scroll.txt";
const TRICKS: [string, string, string, Mode, string][] = [
  // icon, label, text, mode, outfile
  ["🚰", "Pour it down the pipe", "psst, pass the bananas", "pipe", ""],
  ["🪟", "A Notepad file", "﻿hello from notepad", "pipe", ""],
  ["📜", "Shout onto a scroll", "the bananas are mine", "say", SCROLL],
  ["🕳️", "A folder that isn't there", "where did it go", "say", "no/such/folder/scroll.txt"],
];

const shouted = (r: Run | null) => (r?.status === 0 ? r.stdout.replace(/\n$/, "") : null);

export default function Howler({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("please be quiet in the library");
  const [mode, setMode] = useState<Mode>("say");
  const [outfile, setOutfile] = useState("");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);

  const howl = (t = text, m = mode, o = outfile) => {
    const out = o ? `-o ${quote(o)} ` : "";
    if (m === "pipe") go(`${out}-`, t);
    else go(`${out}${quote(t || "''")}`);
  };
  useEffect(() => {
    go(quote("please be quiet in the library"));
  }, [go]);

  const loud = shouted(mine);
  const saved = mine?.status === 0 && outfile && !loud;

  return (
    <div className="toy">
      <div className={styles.stage}>
        <span className={`${styles.monkey} ${busy ? styles.shake : ""}`} aria-hidden="true">
          {bundle.character.emoji}
        </span>
        <p className={`bubble ${styles.shout}`} aria-live="polite">
          {busy && !mine ? "…" : saved ? `📜 Shouted onto ${outfile}!` : (loud ?? "OOH OOH?")}
        </p>
      </div>
      <Oops run={mine} />
      {mine?.stderr.includes("Traceback") && <p className="hint">Howie tripped over and crashed instead of saying sorry.</p>}
      {other?.stderr.includes("Traceback") && !mine?.stderr.includes("Traceback") && (
        <p className="rival">{rivalName(bundle, brain)} would trip over and crash here.</p>
      )}
      {loud != null && loud.startsWith("﻿") && (
        <p className="hint">Psst: there&apos;s an invisible Notepad mark hiding before the first letter!</p>
      )}
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would {other.status === 0 ? "shout" : "say"}:{" "}
          <q>{other.status === 0 ? shouted(other) || `(saved onto ${outfile})` : "Ouch, I crashed!"}</q>
        </p>
      )}
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          howl();
        }}
      >
        <label htmlFor="howl-text">Whisper something to Howie</label>
        <textarea id="howl-text" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <fieldset className={styles.modes}>
          <legend>How does it reach Howie?</legend>
          <label>
            <input type="radio" name="howl-mode" checked={mode === "say"} onChange={() => setMode("say")} /> Say it
          </label>
          <label>
            <input type="radio" name="howl-mode" checked={mode === "pipe"} onChange={() => setMode("pipe")} /> Pour it
            down the pipe 🚰
          </label>
        </fieldset>
        <div className="field-row">
          <label htmlFor="howl-out" className="inline-label">
            Save onto (optional)
          </label>
          <input id="howl-out" value={outfile} placeholder="scroll.txt" onChange={(e) => setOutfile(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            HOWL!
          </button>
        </div>
      </form>
      {saved && (
        <button type="button" className="soft-btn" onClick={() => go(quote(outfile))} disabled={busy}>
          <span aria-hidden="true">📖 </span>Read the scroll back
        </button>
      )}
      <Chips
        items={TRICKS.map(([icon, label]) => [icon, label])}
        onPick={(label) => {
          const [, , t, m, o] = TRICKS.find((x) => x[1] === label)!;
          setText(t);
          setMode(m);
          setOutfile(o);
          howl(t, m, o);
        }}
        label="Things to try"
      />
    </div>
  );
}
