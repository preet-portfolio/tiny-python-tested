"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./jump.module.css";

/* ---------------- Hopscotch hides phone numbers (jump) ---------------- */

const KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", ""];
const PARTNER: Record<string, string> = { "1": "9", "2": "8", "3": "7", "4": "6", "5": "0", "6": "4", "7": "3", "8": "2", "9": "1", "0": "5" };

// Where "0" sits in the digit alphabets people commonly type (ASCII, Arabic, Persian,
// Hindi, Bengali, Thai, full-width and a few more). Only used to light up the keypad.
const ZEROS = [0x30, 0x660, 0x6f0, 0x966, 0x9e6, 0xa66, 0xae6, 0xb66, 0xbe6, 0xc66, 0xce6, 0xd66, 0xe50, 0xed0, 0xf20, 0x1040, 0x17e0, 0x1810, 0xff10];

/** The plain 0-9 value of a digit, whatever alphabet it's written in. */
const plainDigit = (ch: string) => {
  const cp = ch.codePointAt(0) ?? 0;
  const zero = ZEROS.find((z) => cp >= z && cp <= z + 9);
  return zero === undefined ? null : String(cp - zero);
};

export default function Jump({ bundle, run, brain, hasBook }: ToyProps) {
  const [text, setText] = useState("867-5309");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const hop = (t: string) => {
    setText(t);
    if (t) go(quote(t));
  };
  useEffect(() => {
    go("867-5309");
  }, [go]);

  const out = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;
  const used = new Set([...text].map(plainDigit).filter((d): d is string => d !== null));

  return (
    <div className="toy">
      <div className={styles.row}>
        <div className={styles.pad} aria-label="Phone keypad: each digit hops over the 5">
          {KEYS.map((k, i) =>
            k ? (
              <span
                key={i}
                className={`${styles.key} ${used.has(k) ? styles.from : ""} ${[...used].some((d) => PARTNER[d] === k) ? styles.to : ""}`}
              >
                {k}
              </span>
            ) : (
              <span key={i} />
            ),
          )}
        </div>
        <div className={styles.side}>
          <p className="bubble" aria-live="polite">
            <span aria-hidden="true">{bundle.character.emoji} </span>
            {busy && out == null ? "…" : (out ?? "Boing?")}
          </p>
          <Oops run={mine} />
          {differs(mine, other) && other?.status === 0 && (
            <p className="rival">
              {rivalName(bundle, brain)} would hop: <q>{other.stdout.replace(/\n$/, "")}</q>
            </p>
          )}
          {out != null && out === text && /\p{Nd}/u.test(text) && (
            <p className="hint">Uh-oh: some digits didn&apos;t hop, so the secret number leaked!</p>
          )}
          {out != null && (
            <button type="button" className="soft-btn" onClick={() => hop(out)} disabled={busy}>
              <span aria-hidden="true">🔁 </span>Hop it back
            </button>
          )}
        </div>
      </div>
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          hop(text);
        }}
      >
        <label htmlFor="jump-text">A secret phone number (or a whole message)</label>
        <div className="field-row">
          <input id="jump-text" value={text} onChange={(e) => setText(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Hop!
          </button>
        </div>
      </form>
      <Chips items={bundle.examples ?? []} onPick={hop} label="Numbers from around the world" />
    </div>
  );
}
