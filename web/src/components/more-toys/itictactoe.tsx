"use client";

import { useEffect, useState } from "react";
import { explain } from "@/lib/kid";
import type { Run } from "@/lib/py";
import { differs, rivalName, useCompare, type ToyProps } from "../toys";

/* ---------------- Tic and Tac (interactive tic-tac-toe) ---------------- */

type Game = { board: string; message: string; next: string | null; over: boolean };

/** Read what the program printed after the last move: the board, what it said, whose turn. */
function readGame(r: Run | null): Game | null {
  if (!r) return null;
  const out = r.stdout.replace(/\n$/, "");
  const rows = out.split("\n").filter((l) => /^\| /.test(l));
  const last = rows.slice(-3);
  const board = last
    .flatMap((row) => row.split("|").slice(1, 4).map((c) => c.trim()))
    .map((c) => (/^\d$/.test(c) ? "." : c))
    .join("");
  const after = out.slice(out.lastIndexOf("-------------") + 13).split("\n").map((l) => l.trim());
  const said = after.filter((l) => l && !/what is your move/.test(l) && !/^No more moves/.test(l));
  const prompts = [...out.matchAll(/Player ([XO]), what is your move/g)];
  const over = /has won!|call it a draw|You quit/.test(said.join(" "));
  // The toy replays every move each turn, so running out of typed moves at a prompt just means
  // "waiting for you". A brain that crashes there (EOFError) has still printed the board; the
  // rules board is where that crash counts against it. Any other failure is a real crash.
  const waiting = r.status !== 0 && /EOFError/.test(r.stderr) && prompts.length > 0;
  const crashed = r.status !== 0 && !waiting ? `It crashed! (${explain(r) ?? "error"})` : null;
  return {
    board: board.length === 9 ? board : ".........",
    message: crashed ?? said.filter((l) => !/Traceback|Error|File "/.test(l)).pop() ?? "",
    next: over ? null : (prompts[prompts.length - 1]?.[1] ?? "X"),
    over,
  };
}

export default function ITicTacToe({ bundle, run, brain, hasBook }: ToyProps) {
  const [moves, setMoves] = useState<string[]>([]);
  const { mine, other, busy, go } = useCompare(run, brain, hasBook);
  const send = (m: string[]) => {
    setMoves(m);
    go("", m.length ? m.join("\n") + "\n" : "");
  };
  useEffect(() => {
    go("", "");
  }, [go]);

  const game = readGame(mine);
  const theirs = readGame(other);
  const board = game?.board ?? ".........";

  return (
    <div className="toy toy-ref">
      <div className="board-wrap">
        <div className="board" role="grid" aria-label="Noughts and crosses board">
          {[0, 1, 2].map((r) => (
            <div role="row" key={r} className="board-row">
              {[0, 1, 2].map((c) => {
                const i = r * 3 + c;
                const v = board[i];
                return (
                  <button
                    key={i}
                    role="gridcell"
                    type="button"
                    className={`cell cell-${v === "." ? "empty" : v}`}
                    disabled={busy || game?.over}
                    onClick={() => send([...moves, String(i + 1)])}
                    aria-label={`Square ${i + 1}: ${v === "." ? "empty" : v}`}
                  >
                    {v === "." ? "" : v}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
        <div className="ref-side">
          <p className="bubble" aria-live="polite">
            <span aria-hidden="true">{bundle.character.emoji} </span>
            {!game ? "…" : game.message || (game.next ? `Your turn, ${game.next}! Tap a square.` : "")}
          </p>
          {game?.next && !game.over && <p className="turn">Next up: {game.next}</p>}
          {differs(mine, other) && theirs && (theirs.message !== game?.message || theirs.next !== game?.next) && (
            <p className="rival">
              {rivalName(bundle, brain)} would say: <q>{theirs.message || `Your turn, ${theirs.next}!`}</q>
            </p>
          )}
          <div className="field-row">
            <button type="button" className="soft-btn" disabled={busy || moves.length === 0} onClick={() => send(moves.slice(0, -1))}>
              <span aria-hidden="true">↩️ </span>Undo
            </button>
            <button type="button" className="soft-btn" disabled={busy || game?.over} onClick={() => send([...moves, "q"])}>
              <span aria-hidden="true">🏳️ </span>Give up
            </button>
            <button type="button" className="soft-btn" onClick={() => send([])}>
              New game
            </button>
          </div>
          <p className="hint">
            Moves so far: {moves.length ? moves.join(", ") : "none yet"}. Try filling the very last square with a win!
          </p>
        </div>
      </div>
    </div>
  );
}
