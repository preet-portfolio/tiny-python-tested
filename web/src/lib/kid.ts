import type { MutantRow, Run } from "./py";

/** Turn an argparse or Python error into something a ten-year-old can read. */
export function explain(run: Run): string | null {
  if (run.timed_out) return "It got stuck going round and round, so I stopped it.";
  if (run.status === 0) return null;
  const text = run.stderr.trim();
  const err = text.split("\n").reverse().find((l) => /error:|Error|No such file/.test(l)) ?? text.split("\n").pop() ?? "";
  const msg = err.replace(/^.*?error:\s*/, "").replace(/^\w+Error:\s*/, "");
  let m: RegExpMatchArray | null;
  if ((m = msg.match(/invalid int value: '(.*)'/))) return `“${m[1]}” isn't a whole number.`;
  if ((m = msg.match(/invalid choice: '?([^' ]*)'?/))) return `“${m[1]}” isn't one of the choices.`;
  if (/the following arguments are required/.test(msg)) return "I need something to work with!";
  if (/No such file or directory/.test(msg)) return "I can't find that file.";
  if ((m = msg.match(/--cell "(\d)" already taken/))) return `Square ${m[1]} is already taken!`;
  if ((m = msg.match(/is impossible: (.*)/))) return `Impossible! ${m[1][0].toUpperCase()}${m[1].slice(1)}.`;
  if ((m = msg.match(/the game is over: (.*)/))) return `The game's over: ${m[1]}.`;
  if (/must be 9 characters/.test(msg)) return "A board is 9 squares of X, O or a dot.";
  if (/Must provide both/.test(msg)) return "A move needs a player and a square.";
  if (/must be greater than 0/.test(msg)) return "We need at least one bottle to sing about!";
  if (/Traceback/.test(text)) return `The program crashed: ${msg}`;
  return msg || "Something went wrong.";
}

const NAMES = [
  "Gribble", "Snork", "Pip", "Wobble", "Fizz", "Nib", "Bloop", "Skitter", "Grub", "Zib",
  "Mopsy", "Twitch", "Blot", "Smudge", "Crumb", "Fidget", "Glop", "Noodle", "Squib", "Tumble",
];

export const gremlinName = (id: number) => NAMES[id % NAMES.length] + (id >= NAMES.length ? ` ${Math.floor(id / NAMES.length) + 1}` : "");

/** What a gremlin did, in plain words. */
export function prank(m: MutantRow): string {
  switch (m.op) {
    case "comparison":
      return "flipped a comparison around";
    case "boolean":
      return "swapped an AND for an OR";
    case "arithmetic":
      return "swapped a sum the wrong way";
    case "string":
      return `scribbled on the text ${m.before}`;
    case "number":
      return `changed the number ${m.before} to ${m.after}`;
    case "method": {
      const a = m.before.split(".").pop();
      const b = m.after.split(".").pop();
      return `made it use .${b}() instead of .${a}()`;
    }
    case "negate-if":
      return "turned a yes into a no";
    case "swap-branches":
      return "swapped the two answers";
    case "reverse-list":
      return "flipped the coin's sides";
    default:
      return "changed something";
  }
}

/** Quote one argument for the program's command line. */
export const quote = (s: string) => (/^[\w.,:+\-/]+$/.test(s) ? s : `'${s.replace(/'/g, `'\\''`)}'`);

/**
 * Words a kid-facing toy shouldn't print. Some programs build words by rule (rhymes, chopped
 * dictionary words), so they can make rude ones; the program and its tests keep them, and the
 * toys hide them on screen. Stored encoded so the source isn't a list of swear words.
 */
const RUDE = new Set(
  atob("YXJzZSxhc3MsYmFzdGFyZCxiaXRjaCxib2xsb2Nrcyxib25rLGNoaW5rLGNvY2ssY29vbixjcmFwLGN1Y2ssY3VudCxkYW1uLGRpY2ssZHlrZSxmYWcsZnVjayxob21vLGppenosa2lrZSxuaWdnYSxuaWdnZXIscGlzcyxwcmljayxyZXRhcmQsc2hhZyxzaGl0LHNsdXQsc3BpYyxzcHVuayx0aXQsdGl0cyx0d2F0LHdhbmssd2Fua2VyLHdob3Jl").split(","),
);
export const isRude = (word: string) => RUDE.has(word.toLowerCase().replace(/[^a-z]/g, ""));

/** Words that aren't swearing but don't belong on a children's page (from Sir Bluster's book
 * word lists). Hidden on screen like the rude ones. */
const NOT_FOR_KIDS = new Set(
  atob("bGFzY2l2aW91cyxsZWNoZXJvdXMsZmlsdGh5LGZpbHRoc29tZSxqdWRhcyxzYXRhbixzbGF2ZSxsdW5hdGljLGRlZ2VuZXJhdGU=").split(","),
);
const hidden = (word: string) => isRude(word) || NOT_FOR_KIDS.has(word.toLowerCase().replace(/[^a-z]/g, ""));

/** Every toy's output goes through this before it reaches the screen. */
export const maskRude = (text: string) => text.replace(/[A-Za-z]+/g, (w) => (hidden(w) ? "🙊" : w));

/** What a gremlin did, said for a nine-year-old (the moment on each toy's first screen). */
export function gremlinDid(op: string): string {
  switch (op) {
    case "string":
      return "scribbled on one word";
    case "number":
      return "changed one number";
    case "method":
      return "swapped one step for another";
    case "arithmetic":
      return "messed up one sum";
    case "swap-branches":
      return "swapped two answers";
    case "reverse-list":
      return "turned one list back to front";
    default:
      return "flipped one yes into a no";
  }
}
