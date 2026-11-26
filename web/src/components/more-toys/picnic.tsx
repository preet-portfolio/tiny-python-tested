"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./picnic.module.css";

/* ---------------- Pip packs the picnic (picnic) ---------------- */

const START = ["chips", "soda", "cupcakes"];
const TRICKY: [string, string[]][] = [
  ["A capital sneaks in", ["apple", "Banana", "cherries"]],
  ["Fancy French food", ["figs", "éclairs", "apples"]],
  ["Empty boxes", ["", "chips", "   "]],
  ["Chips twice", ["chips", "soda", "Chips"]],
  ["Salt, pepper", ["salt, pepper", "chips", "cake"]],
];

const args = (items: string[], sorted: boolean) =>
  `${sorted ? "-s " : ""}${items.map((i) => quote(i)).join(" ")}`;

export default function Picnic({ bundle, run, brain, hasBook }: ToyProps) {
  const [items, setItems] = useState<string[]>(START);
  const [sorted, setSorted] = useState(false);
  const [next, setNext] = useState("");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);

  const pack = (list: string[], s = sorted) => {
    setItems(list);
    if (list.length) go(args(list, s));
  };
  useEffect(() => {
    go(args(START, false));
  }, [go]);

  const said = mine?.status === 0 ? mine.stdout.trim() : null;

  return (
    <div className="toy">
      <div className={styles.basket} aria-label="The picnic basket">
        <span className={styles.handle} aria-hidden="true" />
        {items.length === 0 && <span className={styles.empty}>The basket is empty!</span>}
        {items.map((item, i) => (
          <button
            key={`${item}-${i}`}
            type="button"
            className={styles.item}
            onClick={() => pack(items.filter((_, j) => j !== i))}
            aria-label={`Take out ${item.trim() || "an empty box"}`}
          >
            {item.trim() ? item : <span className={styles.blank}>(empty box)</span>}
            <span aria-hidden="true"> ✕</span>
          </button>
        ))}
      </div>
      <p className="bubble" aria-live="polite">
        <span aria-hidden="true">{bundle.character.emoji} </span>
        {busy && !said ? "…" : (said ?? (items.length ? "Hmm?" : "Put something in the basket!"))}
      </p>
      <Oops run={mine} />
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would say:{" "}
          <q>{other.status === 0 ? other.stdout.trim() : "Oops, something went wrong!"}</q>
        </p>
      )}
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          pack([...items, next]);
          setNext("");
        }}
      >
        <label htmlFor="picnic-item">What else should Pip pack?</label>
        <div className="field-row">
          <input id="picnic-item" value={next} onChange={(e) => setNext(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Pack it!
          </button>
        </div>
        <label className={styles.sort}>
          <input
            type="checkbox"
            checked={sorted}
            onChange={(e) => {
              setSorted(e.target.checked);
              pack(items, e.target.checked);
            }}
          />{" "}
          Put the list in ABC order
        </label>
      </form>
      <Chips items={bundle.examples ?? []} onPick={(v) => pack([...items, v])} label="Food to add" />
      <p className="hint">Tricky baskets:</p>
      <Chips
        items={TRICKY.map(([label]) => ["🧺", label])}
        onPick={(label) => {
          const list = TRICKY.find((t) => t[0] === label)![1];
          const s = label === "A capital sneaks in" || label === "Fancy French food";
          setSorted(s);
          pack(list, s);
        }}
        label="Tricky baskets"
      />
    </div>
  );
}
