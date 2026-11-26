# Simpler, deeper: one moment in 30 seconds

The site has one idea worth landing: **a toy follows every one of the book's rules, a gremlin
sneaks a change past them, and a real-life rule catches it.** Today a visitor has to do about six
things and learn three words before they see it. This plan cuts the path to zero clicks.

Nothing here is built yet. This document holds the evidence, the decisions to make first, the
cut list, and the low-fidelity first screen.

## 1. Evidence

### What it takes today to reach the moment (cognitive walkthrough, Polly's page)

| Step | What the visitor has to do | New idea they meet | Wait |
|---|---|---|---|
| 1 | Read the home page hero, press "Meet Polly" | toys, rules, gremlins (all at once) | |
| 2 | Choose "Who's playing?" (Book Polly / Clever Polly / Your Polly) | versions ("brains") | |
| 3 | Type or tap a word | | Python download: 2.3 s on fast wifi, **105 s on a slow phone** |
| 4 | Press "Check the rules" | rules = tests | a few seconds |
| 5 | Press "Release the gremlins" | gremlins = changed copies | about 30 s with the tab in front (minutes if it's in the background) |
| 6 | Read the score, find "Escaped", open a gremlin, read code (`before → after`) | code | |

About 6 actions, 3 new ideas and 2–3 waits. The moment itself is in step 6, below the fold.

### Speed (measured, not estimated)

- Lighthouse 12.8.2, mobile, devtools throttling (slow 4G, CPU ×4), Polly's page: performance
  0.82, accessibility 1.0, first and largest paint 3.5 s, total blocking time 100 ms, layout shift
  0, 6,954 KiB. Lighthouse finishes before Python is ready, so it never sees a toy answer.
- Puppeteer, cold cache, same throttling applied to the page **and** the Python worker, timed to
  the `tptl:first-answer` mark: **104.7 s and 18.3 MB**. Unthrottled: 2.3 s.
- Where the bytes go (`web/out/pyodide`, 16 MB): the WebAssembly runtime 9.6 MB, standard library
  2.5 MB, loader 1.25 MB, Pygments 1.23 MB, setuptools 0.76 MB, Hypothesis 0.63 MB, pytest 0.37 MB.

**Conclusion.** The 5-second target can't be met by any page that waits for live Python. The first
screen has to answer from results CI already recorded, and load Python only when the visitor asks
for "Run it live". A toy run alone doesn't need pytest, Hypothesis, Pygments or setuptools (about
3 MB), but even without them the runtime is about 13 MB, roughly 75 s on slow 4G.

### Reading level

Flesch–Kincaid over 407 kid-facing lines: 100 score above grade 4.5. The formula is noisy on short
fragments ("Refuses 'banana' bottles" scores 13.1), so the check in CI should fail full sentences
above grade 4 and list fragments for a person to read.

### Content check

| Toy | What a parent could object to | Proposed decision |
|---|---|---|
| Sir Bluster (insults) | The book's word lists include *lascivious, lecherous, filthy, filthsome, Judas, Satan, ass, slave, lunatic, degenerate*. | Show those words as 🙊 on screen, the way the rhymer hides rude rhymes. The program and tests stay the book's. "Butt" stays: it's the joke. |
| Rocky (rhymer) | Real rhymes include swear words and slurs. | Already filtered ("🙈 3 rude ones hidden"). Move the same filter to **every** toy's output, not one toy. |
| Lexi (Gashlycrumb) | The book's alphabet is about children dying. | The toy already uses a friendly alphabet. The book's version appears only in the test files, which move behind "For grown-ups". |
| The Bottle Choir | The song is about beer. | Your call: keep it as is (it's the traditional song and isn't on the first screen), or leave the choir out of the kids' toy box. Changing "beer" on screen would show output the program didn't produce, so that's out. |
| Shh (passwords) | Random word joins can make rude words. | Already filtered, with a "use a password manager" hint. |

### Think-aloud sessions

The script is in [`THINK_ALOUD.md`](THINK_ALOUD.md): three kids aged 8–12 and two adults who don't
write code, 10 minutes each, on the current site and then on the new screen. **These haven't been
run yet; they need you.** Anything two or more people stall on moves to "Peek inside", moves to
"For grown-ups" or is removed.

## 2. The flagship gremlin

CI's metrics run (`python -m tptl.metrics`, which now also writes `moments.json` through `tptl/moments.py`) runs every chapter's gremlins twice, once against the book's rules
and once against all rules, and kept the ones the book missed and real life caught. That's 105
gremlins across 15 chapters.

| Chapter | Gremlins the book misses that real life catches |
|---|---|
| Polly (a or an) | **31** of 60 |
| Tic and Tac | 26 |
| Mabel (mad libs) | 15 |
| Coach Boing | 7 |
| Lexi | 5 |
| Sir Bluster, Mumbles | 4 each |
| Pip, Howie | 3 each |
| Brother Biscuit | 2 |
| Choir, Percy, Rocky, Scramble, Ref Robo | 1 each |

**Flagship: Polly, the gremlin that crosses "hour" off her list of words with a shy h.**

- It's the most surprising: Polly passes all 6 of the book's rules and still lets 31 of 60
  gremlins through, more than any other toy.
- It's the most explainable. Most of Polly's 31 change a word a child can say out loud ("hour",
  "honest", "unicorn", "one"). Tic and Tac's 26 are about game state, and Mabel's need a story file.
- Within Polly, "hour" wins over "unicorn" and "one" because it fails in the most obvious way and
  the fix is one word. Checked by running both: the real Polly says
  `Ahoy, Captain, an hour off the larboard bow!`; the gremlin says
  `Ahoy, Captain, a hour off the larboard bow!`. Both say `an octopus` and `a narwhal`, which is
  all the book's rules ask about.
- The rule that catches it: "An hour, not a hour (the h is shy)" (`test_silent_h`).

Kid version, for the screen: *"A gremlin rubbed out one word in Polly's head. Now she says 'a
hour'. The book's 6 rules never ask about 'hour', so they didn't spot it. The real-life rule did."*

### A problem the data turned up, and the fix

Gremlin counts changed between runs (Sir Bluster's real-life rules caught 39 in one run and 40 in
another; Tic and Tac and Ref Robo moved too). Two causes, both in how tests run, not in the tests:

- Some tests load a program and call it inside the test process, so the program read the
  command line of whatever started the run (the CI script, a one-off script, the browser).
  `tptl.runner` now gives every test run a clean `sys.argv`.
- The book's tests pick random words and boards, and programs run without `--seed` seed from the
  clock. `tptl.runner` now seeds each test by its name, and maps an unseeded program to a fixed
  seed, only while tests run. Toys you play with keep real randomness.

- Even then, gremlins from one chapter could leave state that nudged a later chapter's count
  when many chapters ran in one process. CI now measures each chapter in a fresh Python process,
  the way the browser gives each page its own Python.

Checked: Tic and Tac measured twice in fresh processes gave 34 and 57 both times, and Ref Robo
56 and 57, matching the full run.

## 3. Cut list

Keep = on the first screen. Peek = behind "Peek inside". Grown-ups = behind "For grown-ups".

### Home page

| Element | Decision | Why |
|---|---|---|
| Wordmark "Tiny Python Toybox" | Keep | |
| Hero headline and paragraph | Remove | The first screen shows it instead of saying it. |
| "Meet Polly" button | Remove | Polly *is* the first screen. |
| Row of character faces | Move to the toy box | |
| "How it works" (three steps) | Remove | The moment is the explanation. |
| Toy box grid | Keep, below the first screen | Each tile: face, name, one line. |
| "The tests are the spec" section, score bars | Grown-ups | Numbers read from CI's JSON. |
| Fine print (Python version, shim, CI check) | Grown-ups | |

### Each toy's page (and the first screen, which is Polly's)

| Element | Decision | Why |
|---|---|---|
| Character face, name, role | Keep | |
| Breadcrumb | Keep (small) | |
| Tagline | Remove | The prediction question does its job. |
| **"Who's playing?" version picker** | **Remove** | Visitors had to understand versions before the toy did anything. The toy is always the one that follows the book's rules. The book's own version moves to Grown-ups and "Your Polly" moves to Peek. |
| Toy card | Keep, trimmed to one input and one answer | |
| Word chips (try these) | Keep | Each chip has a CI-recorded answer, so it shows instantly. |
| Free typing | Keep, live | Typing your own word loads Python ("Waking Polly up…"). |
| "Check the rules" button | Remove | The CI result is already on screen. "Run it live" redoes it. |
| Two full rule lists | Peek | The screen shows "follows all 6 book rules ✓" and the one real-life rule that catches the gremlin. |
| Gremlin attack: progress bar, tally, caught and escaped lists | Peek, live | The screen shows one gremlin. The full run is "Run it live". |
| Gremlin card with `before → after` code | Peek | The screen says it in words. |
| Score ("22 of 60 caught") | Grown-ups | |
| "Peek inside Polly's brain" editor | Peek (as now) | |
| "For grown-ups: what's going on" | Keep, collapsed | |
| Next-toy link | Keep | |

### The other 20 toys

Same frame as the first screen, from the same CI file: one input, one answer, one gremlin moment.
Six chapters have no gremlin that the book misses and real life catches (Hopscotch, Professor Hoot,
Melody, Whiskers, Annie, Shh). Their moment is the honest one: "the book's rules caught every
gremlin". They don't get an invented one.

## 4. What was built

1. **CI records each toy's moment.** `python -m tptl.metrics` measures each chapter in a fresh
   Python process and writes `moments.json` next to `summary.json`, from the same gremlin runs. Per
   toy: rule counts, gremlin counts, the real program's recorded answer to each example, and the
   flagship gremlin with its recorded answer and the rule that catches it. The choice is made by
   `tptl/moments.py`: changed words first, then numbers, then the rest, preferring a gremlin that
   says something wrong over one that crashes. Lexi's examples use the friendly alphabet
   (`moment_args` in her `chapter.json`).
2. **The first screen** (`ToyStage.tsx`) reads only that file: Guess, Try, Gremlin!, then
   "Run it live". The home page shows the toy where the book's rules miss the most gremlins that
   real life catches (`flagship()` in `lib/data.ts`), which is Polly.
3. **`npm run build` checks the pages** (`scripts/check-moments.mjs`, run after every build): the
   counts in `moments.json` must equal `summary.json`, and each toy's page must show its recorded
   lines and counts.
4. **Python loads only on "Run it live"**, and pytest and Hypothesis load only when someone checks
   the rules or sends in gremlins.
5. **The version picker is gone.** The toy is always the one that passes every rule. The book's
   version is a link under "For grown-ups"; "Your Polly" is under "Peek inside".
6. **Unsuitable words are hidden in every toy's output** (`maskRude` in `lib/kid.ts`), including
   Sir Bluster's word list.

Not done: the think-aloud sessions (they need real people), and an automatic reading-level check.
