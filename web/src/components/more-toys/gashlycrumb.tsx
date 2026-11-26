"use client";

import { useEffect, useState } from "react";
import { quote } from "@/lib/kid";
import { Chips, Oops, differs, rivalName, useCompare, type ToyProps } from "../toys";
import styles from "./gashlycrumb.module.css";

/* ---------------- Lexi's alphabet scrapbook (gashlycrumb) ---------------- */

// Lexi's own scrapbook, piped in with "-f -" so the toy never shows the book's gloomy one.
const KIND = `A is for Alpaca who dances all day.
B is for Bear who loves honey and hay.
C is for Cat who naps in the sun.
D is for Dog who thinks fetching is fun.
E is for Eel who glows in the dark.
F is for Frog who sings in the park.
G is for Goat who climbs up the hill.
H is for Hen who sits very still.
I is for Ibis who fishes with care.
J is for Jay with a crest in her hair.
K is for Koala who hugs every tree.
L is for Llama, and that llama is me!
M is for Mouse who nibbles on cheese.
N is for Newt who naps in the breeze.
O is for Owl who reads books at night.
P is for Panda, all black and all white.
Q is for Quail who quietly hums.
R is for Rabbit who drums with her thumbs.
S is for Seal who juggles a ball.
T is for Tortoise, the slowest of all.
U is for Unicorn, sparkly and bright.
V is for Vole who tunnels all night.
W is for Whale who sings to the sea.
X is for Xerus, a squirrel, carefree.
Y is for Yak with a coat long and warm.
Z is for Zebra who stripes every storm.
`;

// The same scrapbook as a person might really save it: a Notepad mark, a note, indents.
const MESSY = "﻿# Lexi's scrapbook (do not eat)\n" + KIND.split("\n").map((l, i) => (i % 3 === 1 ? `   ${l}` : l)).join("\n");

const letters = (name: string) => [...name].filter((c) => c.trim());

export default function Gashlycrumb({ bundle, run, brain, hasBook }: ToyProps) {
  const [name, setName] = useState("SAM");
  const [messy, setMessy] = useState(false);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const look = (n = name, m = messy) => {
    const ls = letters(n);
    if (ls.length) go(`-f - ${ls.map(quote).join(" ")}`, m ? MESSY : KIND);
  };
  useEffect(() => {
    go("-f - S A M", KIND);
  }, [go]);

  const pages = mine?.status === 0 ? mine.stdout.replace(/\n$/, "").split("\n") : [];
  const otherPages = other?.status === 0 ? other.stdout.replace(/\n$/, "").split("\n") : [];

  return (
    <div className="toy">
      <form
        className="toy-form"
        onSubmit={(e) => {
          e.preventDefault();
          look();
        }}
      >
        <label htmlFor="lexi-name">Type a name, and Lexi finds a page for each letter</label>
        <div className="field-row">
          <input id="lexi-name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="off" />
          <button type="submit" className="big-btn" disabled={busy}>
            Find the pages!
          </button>
        </div>
        <label className={styles.toggle}>
          <input
            type="checkbox"
            checked={messy}
            onChange={(e) => {
              setMessy(e.target.checked);
              look(name, e.target.checked);
            }}
          />{" "}
          Use the messy scrapbook (a hidden Notepad mark, a note and wobbly indents)
        </label>
      </form>
      <Chips
        items={bundle.examples ?? []}
        onPick={(n) => {
          setName(n);
          look(n);
        }}
        label="Names to look up"
      />
      <Oops run={mine} />
      <div className={styles.book} aria-live="polite">
        {pages.map((p, i) => {
          const unknown = p.startsWith("I do not know");
          const theirs = otherPages[i];
          return (
            <div key={i} className={`${styles.page} ${unknown ? styles.missing : ""}`}>
              <span className={styles.big} aria-hidden="true">
                {unknown ? "?" : p[0]}
              </span>
              <span>{unknown ? `${bundle.character.emoji} ${p}` : p}</span>
              {differs(mine, other) && theirs !== undefined && theirs !== p && (
                <small className="rival">
                  {rivalName(bundle, brain)}: <q>{theirs}</q>
                </small>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
