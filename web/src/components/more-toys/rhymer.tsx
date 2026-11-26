"use client";

import { useEffect, useState } from "react";
import { isRude, quote } from "@/lib/kid";
import type { Run } from "@/lib/py";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./rhymer.module.css";

/* ---------------- Rocky the rapping raccoon (rhymer) ---------------- */

const allRhymes = (r: Run | null) =>
  r?.status === 0 && !r.stdout.startsWith("Cannot rhyme") ? r.stdout.trim().split("\n").filter(Boolean) : [];
/** Rhyming by rule makes a few rude words; the program keeps them, the toy doesn't show them. */
const rhymesOf = (r: Run | null) => allRhymes(r).filter((w) => !isRude(w) && w !== "🙊");

/** The ending every rhyme shares: the longest common tail of the list. */
function sharedEnd(words: string[]): string {
  if (words.length < 2) return "";
  let end = words[0];
  for (const w of words) while (!w.endsWith(end)) end = end.slice(1);
  return end;
}

export default function Rhymer({ bundle, run, brain, hasBook }: ToyProps) {
  const [word, setWord] = useState("cake");
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const rap = (w: string) => {
    setWord(w);
    go(quote(w || "''"));
  };
  useEffect(() => {
    go("cake");
  }, [go]);

  const words = rhymesOf(mine);
  const hidden = allRhymes(mine).length - words.length;
  const theirs = rhymesOf(other);
  const end = sharedEnd(words);
  const cannot = mine?.status === 0 && mine.stdout.startsWith("Cannot rhyme");
  const onlyTheirs = theirs.filter((w) => !words.includes(w));

  return (
    <div className="toy">
      <p className="bubble" aria-live="polite">
        {busy && !mine
          ? "…"
          : cannot
            ? `${bundle.character.emoji} Yo… I got nothing for that one.`
            : words.length
              ? `${bundle.character.emoji} ${words.slice(0, 4).join(", ")}… yeah!`
              : "Drop me a word!"}
      </p>
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          rap(word);
        }}
      >
        <label htmlFor="rhyme-word">Give Rocky a word</label>
        <div className="field-row">
          <input id="rhyme-word" value={word} onChange={(e) => setWord(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Rap it!
          </button>
        </div>
      </form>
      <Chips items={bundle.examples ?? []} onPick={rap} label="Words to try" />
      <Oops run={mine} />
      {words.length > 0 && (
        <>
          <p className={styles.count}>
            {words.length} rhymes{end && <>, all ending in “{end}”</>}
            {hidden > 0 && (
              <>
                {" "}
                <span aria-hidden="true">🙈</span> ({hidden} rude {hidden === 1 ? "one" : "ones"} hidden)
              </>
            )}
          </p>
          <div className={styles.cloud} aria-live="polite">
            {words.map((w, i) => (
              <span key={w} className={styles.word} style={{ animationDelay: `${Math.min(i, 40) * 12}ms` }}>
                <span className={styles.front}>{end ? w.slice(0, w.length - end.length) : w}</span>
                <span className={styles.rest}>{end}</span>
              </span>
            ))}
          </div>
        </>
      )}
      {differs(mine, other) && other?.status === 0 && (
        <p className="rival">
          {rivalName(bundle, brain)}{" "}
          {theirs.length === 0 ? (
            <>
              would say: <q>{other.stdout.trim()}</q>
            </>
          ) : onlyTheirs.length ? (
            <>
              would also rap: <q>{onlyTheirs.slice(0, 8).join(", ")}</q>
            </>
          ) : (
            <>would rap {theirs.length} rhymes instead of {words.length}.</>
          )}
        </p>
      )}
    </div>
  );
}
