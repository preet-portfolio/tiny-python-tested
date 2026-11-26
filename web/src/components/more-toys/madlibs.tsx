"use client";

import { useEffect, useMemo, useState } from "react";
import { explain, quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./madlibs.module.css";

/* ---------------- Mabel the storytelling llama (mad libs) ---------------- */

const BLANK = /<([^<>\s](?:[^<>]*[^<>\s])?)>/g;
const EXTRA: [string, string, string][] = [
  ["📦", "a parcel", "Hi <first name>, your <thing> is on its way to <place>!"],
  ["🧮", "a maths fact", "I know 5 < 6 and 7 > 3, said the <animal>."],
  ["🐸", "a fairy tale", "A <noun> met a <noun> and they both said <exclamation>!"],
];
const article = (w: string) => (/^[aeiou]/i.test(w) ? "an" : "a");

export default function MadLibs({ bundle, run, brain, hasBook }: ToyProps) {
  const stories = useMemo(() => {
    const fromBook = Object.entries(bundle.files)
      .filter(([name]) => /^inputs\/.+\.txt$/.test(name) && !/no_blanks/.test(name))
      .map(([name, text]): [string, string, string] => ["📖", name.replace(/^inputs\/|\.txt$/g, ""), text.trimEnd()]);
    return [...EXTRA, ...fromBook];
  }, [bundle.files]);
  const [story, setStory] = useState(stories[0][2]);
  const names = useMemo(() => [...story.matchAll(BLANK)].map((m) => m[1]), [story]);
  const [answers, setAnswers] = useState<string[]>([]);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  useEffect(() => setAnswers((a) => names.map((_, i) => a[i] ?? "")), [names]);

  const tell = () => go(`- -i ${names.map((_, i) => quote(answers[i] ?? "")).join(" ")}`, story);
  const told = mine?.status === 0 ? mine.stdout.replace(/\n$/, "") : null;

  return (
    <div className="toy">
      <p className="chips-label">Pick a story with holes in it:</p>
      <Chips
        items={stories.map(([icon, label]) => [icon, label])}
        onPick={(label) => setStory(stories.find((s) => s[1] === label)![2])}
        label="Stories"
      />
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          tell();
        }}
      >
        <label htmlFor="mad-story">The story (put a hole in &lt;angle brackets&gt;)</label>
        <textarea id="mad-story" rows={3} value={story} onChange={(e) => setStory(e.target.value)} />
        {names.length > 0 ? (
          <div className={styles.blanks}>
            {names.map((name, i) => (
              <label key={i} className={styles.blank}>
                Give me {article(name)} {name}
                <input
                  value={answers[i] ?? ""}
                  onChange={(e) => setAnswers((a) => a.map((v, j) => (j === i ? e.target.value : v)))}
                  autoComplete="off"
                />
              </label>
            ))}
          </div>
        ) : (
          <p className="hint">This story has no holes yet. Add one like &lt;animal&gt;.</p>
        )}
        <div className="field-row">
          <button type="submit" className="big-btn" disabled={busy}>
            Tell the story!
          </button>
          <button type="button" className="soft-btn" onClick={() => go("- -i " + quote(answers[0] ?? "x"), story)}>
            <span aria-hidden="true">🙊 </span>Forget some words
          </button>
        </div>
      </form>
      <Oops run={mine} />
      {told != null && (
        <p className={styles.story} aria-live="polite">
          <span aria-hidden="true">{bundle.character.emoji} </span>
          {told}
        </p>
      )}
      {differs(mine, other) && other && (
        <p className="rival">
          {rivalName(bundle, brain)} would say: <q>{other.status === 0 ? other.stdout.trim() : explain(other)}</q>
        </p>
      )}
    </div>
  );
}
