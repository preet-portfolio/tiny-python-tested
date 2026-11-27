import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import type { Bundle } from "./py";
import FLAGSHIP from "@/data/flagship.json";

const PUBLIC = path.join(process.cwd(), "public");

export type Summary = {
  generated: string;
  python: string;
  chapters: {
    id: string;
    tests: { book: number; world: number; passed: number; total: number };
    mutation: Record<"book" | "world", { killed: number; total: number }>;
  }[];
};

export type Parity = {
  python: string;
  mismatches: number;
  rows: { chapter: string; variant: string; tests: number; commands_compared: number }[];
};

function readJSON<T>(rel: string): T | null {
  const p = path.join(PUBLIC, rel);
  return existsSync(p) ? (JSON.parse(readFileSync(p, "utf8")) as T) : null;
}

export const builtChapters = () =>
  readJSON<{ id: string }[]>("chapters/index.json")?.map((c) => c.id) ?? [];
export const loadBundle = (id: string) => readJSON<Bundle>(`chapters/${id}.json`);
export const loadSummary = () => readJSON<Summary>("metrics/summary.json");
export const loadParity = () => readJSON<Parity>("metrics/parity.json");

/** One toy's gremlin moment, recorded by CI (python/tptl/moments.py). */
export type Chip = { args: string; label: string; status: number; stdout: string };
export type MomentEntry = {
  id: string;
  character: { name: string; emoji: string; role: string };
  /** ci_only: book rules that need a text we can't share, so only CI runs them. */
  rules: { book: number; real_life: number; ci_only?: number };
  gremlins: { total: number; book_caught: number; all_caught: number; book_missed_real_life_caught: number };
  chips: Chip[];
  moment: {
    op: string;
    line: number;
    before: string;
    after: string;
    caught_by: string[];
    rules: string[];
    args?: string;
    label?: string;
    real?: { status: number; line: string };
    gremlin?: { status: number; line: string };
  } | null;
};
export type Moments = { generated: string; python: string; chapters: MomentEntry[] };

export const loadMoments = () => readJSON<Moments>("metrics/moments.json");
export const loadMoment = (id: string) => loadMoments()?.chapters.find((c) => c.id === id) ?? null;

/** The first screen's toy, chosen by hand in src/data/flagship.json (see its "why"). Only a toy
 * whose recorded gremlin says something wrong, rather than crashing, can be shown; the build
 * check fails if the chosen one isn't. */
export function flagship(m: Moments | null): MomentEntry | null {
  const c = m?.chapters.find((x) => x.id === FLAGSHIP.id);
  return c?.moment?.real?.status === 0 && c.moment.gremlin?.status === 0 ? c : null;
}
