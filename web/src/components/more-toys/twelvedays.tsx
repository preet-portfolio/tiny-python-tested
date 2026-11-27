"use client";

import { useEffect, useState } from "react";
import type { Run } from "@/lib/py";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./twelvedays.module.css";

/* ---------------- Percy the partridge (twelve_days) ---------------- */

const GIFTS: [string, string][] = [
  ["🍐", "partridge"],
  ["🕊️", "turtle doves"],
  ["🐔", "French hens"],
  ["🐤", "calling birds"],
  ["💍", "gold rings"],
  ["🪿", "geese"],
  ["🦢", "swans"],
  ["🥛", "maids"],
  ["💃", "ladies"],
  ["🤴", "lords"],
  ["🎶", "pipers"],
  ["🥁", "drummers"],
];

const lineEndings = (r: Run | null) => (r?.status === 0 ? (r.stdout.match(/\n/g) ?? []).length : 0);

export default function TwelveDays({ bundle, run, brain, hasBook }: ToyProps) {
  const [day, setDay] = useState(3);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const sing = (n: string) => {
    const d = parseInt(n, 10);
    if (d >= 1 && d <= 12) setDay(d);
    go(`-n ${n.trim() || "''"}`);
  };
  useEffect(() => {
    go("-n 3");
  }, [go]);

  const ok = mine?.status === 0;
  const verses = ok ? mine.stdout.replace(/\n+$/, "").split("\n\n") : [];
  const sung = verses.length;
  const totalGifts = (sung * (sung + 1) * (sung + 2)) / 6;

  return (
    <div className="toy">
      <p className="bubble" aria-live="polite">
        {busy && !mine ? "…" : ok ? `${bundle.character.emoji} Tweet! ${sung} ${sung === 1 ? "day" : "days"} of song, coming up!` : "Hmm?"}
      </p>
      <div className={styles.days} role="group" aria-label="Pick a day">
        {GIFTS.map(([icon, name], i) => (
          <button
            key={name}
            type="button"
            className={styles.day}
            aria-pressed={day === i + 1}
            disabled={busy}
            onClick={() => sing(String(i + 1))}
          >
            <span className={styles.dayIcon} aria-hidden="true">
              {icon}
            </span>
            Day {i + 1}
          </button>
        ))}
      </div>
      <p className="chips-label">Or try a day that isn&apos;t on the calendar:</p>
      <Chips items={[["🤔", "0"], ["😱", "13"], ["🍌", "banana"]]} onPick={sing} label="Odd days" />
      <Oops run={mine} />
      {ok && (
        <div className={styles.pile} aria-label={`A pile of ${totalGifts} presents`}>
          <p className={styles.total}>
            Presents so far: {totalGifts} <span aria-hidden="true">🎁</span>
          </p>
          {Array.from({ length: sung }, (_, k) => sung - 1 - k).map((g) => (
            <div key={`${sung}-${g}`} className={styles.pileRow} aria-hidden="true">
              {Array.from({ length: g + 1 }, (_, j) => (
                <span key={j} style={{ animationDelay: `${(sung - g) * 60 + j * 25}ms` }}>
                  {GIFTS[g][0]}
                </span>
              ))}
            </div>
          ))}
        </div>
      )}
      {differs(mine, other) && other?.status === 0 && (
        <p className="rival">
          {rivalName(bundle, brain)} sings the same words, but its song ends without the final Enter. Saved as a file, a
          line counter finds {lineEndings(other)} lines instead of {lineEndings(mine)}, so it doesn&apos;t match the saved
          copy.
        </p>
      )}
      {/* The songbook scrolls on long songs, so it must take keyboard focus (axe: scrollable-region-focusable). */}
      {verses.length > 0 && (
        <div className="songbook" aria-live="polite" tabIndex={0} role="region" aria-label="The song">
          <p className="songbook-count">
            {verses.length} {verses.length === 1 ? "verse" : "verses"}, {lineEndings(mine)} lines
          </p>
          <ol>
            {verses.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
