"use client";

export type Run = {
  argv: string[];
  status: number;
  stdout: string;
  stderr: string;
  timed_out: boolean;
};

export type TestRow = {
  nodeid: string;
  name: string;
  file: string;
  outcome: "passed" | "failed" | "skipped";
  duration: number;
  message: string;
  detail: string;
  runs: Run[];
  run_count: number;
};

export type TestResult = {
  exit_code: number;
  passed: number;
  failed: number;
  total: number;
  tests: TestRow[];
  log: string;
};

export type MutantRow = {
  id: number;
  op: string;
  line: number;
  col: number;
  before: string;
  after: string;
  killed: boolean;
  killed_by: string[];
  timed_out: boolean;
};

export type MutationResult =
  | { error: string; baseline: TestResult }
  | { tests: string[]; mutants: MutantRow[]; killed: number; total: number; score: number | null };

export type Bundle = {
  id: string;
  number: number;
  title: string;
  program: string;
  mechanic: string;
  scenario: { title: string; body: string };
  world_label?: string;
  note?: string;
  shared_inputs?: string[];
  toy: string;
  character: { name: string; emoji: string; role: string };
  tagline: string;
  brains: { book?: string; real: string };
  brain_blurbs: { book?: string; real: string };
  rules: Record<string, string>;
  examples?: [string, string][];
  book: string | null;
  upstream_tests: string[];
  scenario_tests: string[];
  try_args: string[];
  files: Record<string, string>;
  starter: string;
  reference: string;
};

type Pending = { resolve: (v: unknown) => void; reject: (e: Error) => void };
export type Progress = { stage: string; i?: number; n?: number };

/** A Pyodide worker with a promise per request. Terminate and recreate to recover. */
export class Python {
  private worker: Worker;
  private seq = 0;
  private pending = new Map<number, Pending>();
  onProgress: (p: Progress) => void = () => {};

  constructor() {
    this.worker = new Worker("/py-worker.js", { type: "module" });
    this.worker.onmessage = (e: MessageEvent) => {
      const msg = e.data;
      if (msg.type === "progress") return this.onProgress(msg);
      const p = this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      if (msg.ok) p.resolve(msg.result);
      else p.reject(new Error(msg.error));
    };
  }

  call<T>(type: string, args: object = {}): Promise<T> {
    const id = ++this.seq;
    return new Promise<T>((resolve, reject) => {
      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject });
      this.worker.postMessage({ id, type, ...args });
    });
  }

  terminate() {
    this.worker.terminate();
    for (const p of this.pending.values()) p.reject(new Error("Python was restarted."));
    this.pending.clear();
  }
}
