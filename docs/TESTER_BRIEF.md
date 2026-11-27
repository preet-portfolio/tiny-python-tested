# Tester brief: Tiny Python Projects, tested live

For 2–3 subagent testers of the **deployed** site. Each tester takes one persona, works only
in the browser (plus a terminal for persona B), and reports findings in the format at the end.
Don't fix anything; report it. Test the URL you are given, not a local build.

Shared setup: a fresh browser profile, desktop 1440×900 unless a step says otherwise. Note the
page URL, browser and time of every finding. The site is built for kids; the technical numbers
live in the "for grown-ups" section of each page.

## A. The 10-year-old who doesn't code

You are 10. You read well but you have never programmed. You skip anything that looks like
grown-up text. You click what looks fun.

Rules for this tester:
- Start a stopwatch when the toy's page has finished loading ("Downloading Python" gone).
- You may not open the "for grown-ups" section, read code, or use the editor.
- Write down every word you'd have to ask a grown-up about (e.g. "argument", "stdout",
  "seed", "exit code", "pytest", "mutant", "STDIN", "flag").

Tasks per toy (from the home page, find the toy by its character, not its chapter number):

| Toy | Find out what it does | Make it do something funny |
|---|---|---|
| Polly 🦜 (Crow's Nest) | Say in your own words what Polly's job is | Make Polly say something wrong or silly ("an unicorn"? "a hour"?), then switch to the cleverer Polly and see her get it right |
| Bottle Choir 🍾 | Say what the choir sings and when it stops | Make the choir sing a very short song (1 or 2 bottles) and a silly-long one; try a number they refuse (0, 2.5, "banana") |
| Whiskers 🐱 | Say what a ransom note is here and what the lucky number does | Write your own demand ("GIVE ME TUNA"), get a note, then get the *same* note again with the same lucky number, and a different one with another number |
| Professor Hoot 🦉 | Say what Hoot counts | Paste something with emoji or "café" and find a count that surprises you |
| Ref Robo 🤖 | Say what Ref Robo checks | Play a few moves; then try to cheat (two winners, X plays twice) and get Robo to object |
| Any new chapter | Same question: what does this character do? | Find one thing that makes it do something unexpected |

Pass, per toy: within **60 seconds** you can (1) say what the toy does in one sentence and
(2) make it produce a visible result you chose, **without** meeting a word from the list above
outside the grown-ups section. Fail: over 60 s, a dead end (nothing happens, an error in
grown-up language, a spinner that never ends), or jargon needed to get going.
Also report: anything scary or mean in the text, buttons too small to tap, and the moment
you'd have given up.

## B. The skeptical engineer

You assume every claim is marketing until you reproduce it. You have a terminal, Python 3.14,
git and Node 24, and the public repo.

Verify the claims:
1. **Book's tests unchanged.** Clone github.com/kyclark/tiny_python_projects at `bcf4b24`.
   For every chapter on the site, `diff` its `test.py` (and `unit.py`, inputs) against
   `python/upstream/<chapter>/` and against the test text the page shows. Pass: no difference
   at all (whitespace included), except `07_gashlycrumb/test.py`: `test_a`, `test_b_c` and
   `test_y` compare SHA-256 digests instead of quoting Gorey. Pass there: the digest of each
   book expected string equals the one in the file, and nothing else differs.
2. **Numbers match the JSON.** For each chapter, every number on the page (tests, passes,
   gremlins/mutants caught, coverage, parity counts) appears in `/metrics/summary.json`,
   `/metrics/parity.json`, `/metrics/coverage.json` or `/metrics/pyodide.json` on the same
   deploy. Pass: every number traced to a field. Fail: any number you can't trace.
3. **Nothing hand-typed.** In the repo, search `web/src` for numeric literals that look like
   results (counts, percentages). Pass: all numbers on the page come from the JSON or the
   in-browser run. Check git history: metrics commits come from the CI bot.
4. **Same seed, same note.** For Whiskers, run `python ransom.py -s N 'TEXT'` natively for
   at least 5 seeds (include 0, a large one like 123456789, and text with ß, İ, emoji) and
   compare with the browser's output for the same inputs. Pass: byte-identical.
5. **Gremlin counts match CI.** Run the mutation tester in the page on the reference solution
   and compare killed/total with `summary.json` and with the latest CI run's artifact.
   Pass: identical. Check that the page's Python version matches `pyodide.json`.

Try to break it (each: page should stay usable, show a plain message, and recover):
- "Your version": `while True: pass`; deep recursion; `print("x" * 10**8)`; `import os;
  os._exit(0)`; `sys.exit("bye")`; reading a file that doesn't exist; deleting the program's
  own file.
- Huge input: paste 5 MB of text into Hoot / Whiskers; a 10,000-digit bottle count.
- Weird unicode: RTL text, combining marks, zero-width joiner emoji, lone surrogates via
  paste, NUL characters, `\r\n` line endings.
- Rapid clicking: click Run / Test / Mutate 20 times fast; switch toys mid-run.
- Offline after load: load a toy, go offline (DevTools), use every control, then open
  another toy. Expected: already-loaded toys keep working; a new one says it needs a
  connection rather than hanging.
- Back/forward and reload mid-run; two tabs at once.

Pass: no frozen tab longer than ~10 s (the line budget should stop loops), no uncaught
error in the console, no stale result shown as current, no output from one toy appearing in
another.

## C. Accessibility and phone tester

Run on the home page and every toy page.
- **axe** (DevTools extension or `npx @axe-core/cli <url>`): pass = 0 serious or critical.
- **Keyboard only**: Tab through every control; everything reachable, visible focus ring,
  logical order, no trap (the code editor must let you Tab or Esc out), Enter/Space activate
  buttons, results announced or focus moved sensibly.
- **Screen reader** (VoiceOver or NVDA): every button, toggle and input has a name that says
  what it does ("Run Polly", not "Button"); emoji characters aren't read as noise or have a
  label; test results and run output are announced (live region) or reachable.
- **375 px width** (and 320 px): no horizontal scroll on the page body (code blocks may
  scroll inside themselves), tap targets ≥ 44×44 px, text ≥ 16 px for body copy.
- **Reduced motion** (`prefers-reduced-motion: reduce`): no animation beyond simple fades.
- **Contrast**: AA for text in light and dark mode.
- **Lighthouse**, phone and desktop, on the home page and two toys. Record Performance,
  Accessibility, Best Practices, SEO. Pass: Accessibility 100, others ≥ 90; report LCP and
  CLS and how large the Pyodide download is before a toy works.

## Finding format

One block per finding, most severe first:

```
### <short title>
- Page: <URL>
- Persona: A | B | C
- Steps: 1. … 2. … 3. …
- Expected: …
- Actual: … (paste output, screenshot path or console text)
- Severity: blocker | major | minor | nit
```

Severity: **blocker** = a persona can't complete a task, a claim is false, or data is wrong;
**major** = completes it only with help or a workaround; **minor** = friction or confusing
words; **nit** = polish. End with a one-line verdict per persona: pass or fail, and why.
