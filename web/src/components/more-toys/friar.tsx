"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";

/* ---------------- Brother Biscuit (friar) ---------------- */

/** Split text into words and the bits between, marking the words that changed. */
function marked(before: string, after: string) {
  const a = before.split(/(\s+)/);
  const b = after.split(/(\s+)/);
  if (a.length !== b.length) return [{ text: after, changed: false }];
  return b.map((text, i) => ({ text, changed: text !== a[i] }));
}

export default function Friar({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("Are you cooking supper?");
  const [said, setSaid] = useState("Are you cooking supper?");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const talk = (t: string) => {
    setText(t);
    setSaid(t);
    go(quote(t || "''"));
  };
  useEffect(() => {
    go(quote("Are you cooking supper?"));
  }, [go]);
  const out = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;

  return (
    <div className="toy">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          talk(text);
        }}
      >
        <label htmlFor="friar-text">Say something to Brother Biscuit</label>
        <textarea id="friar-text" rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="field-row">
          <button type="submit" className="big-btn" disabled={busy}>
            Say it his way!
          </button>
        </div>
      </form>
      <Chips items={bundle.examples ?? []} onPick={talk} label="Things to say" />
      <Oops run={mine} />
      {out != null && (
        <p className="bubble" aria-live="polite">
          <span aria-hidden="true">{bundle.character.emoji} </span>
          {marked(said, out).map((p, i) =>
            p.changed ? (
              <mark key={i} style={{ background: "var(--sun)", color: "#1f2a44", borderRadius: 6, padding: "0 4px" }}>
                {p.text}
              </mark>
            ) : (
              <span key={i}>{p.text}</span>
            ),
          )}
        </p>
      )}
      {differs(mine, other) && other?.status === 0 && (
        <p className="rival">
          {rivalName(bundle, brain)} would say: <q>{other.stdout.trim()}</q>
        </p>
      )}
    </div>
  );
}
