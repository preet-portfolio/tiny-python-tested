import Link from "next/link";
import { ToyStage } from "@/components/ToyStage";
import { BOOK } from "@/data/book";
import { builtChapters, flagship, loadBundle, loadMoments, loadParity } from "@/lib/data";

export default function Home() {
  const built = new Set(builtChapters());
  const toys = BOOK.filter((c) => built.has(c.id))
    .map((c) => loadBundle(c.id))
    .filter((b) => b !== null);
  const moments = loadMoments();
  const parity = loadParity();
  // The first screen's toy is picked by CI's data, not by hand (see flagship()).
  const star = flagship(moments);
  const starBundle = star ? loadBundle(star.id) : null;
  const shown = moments?.chapters.filter((c) => built.has(c.id)) ?? [];
  const totals = shown.reduce(
    (acc, c) => ({
      book: acc.book + c.gremlins.book_caught,
      all: acc.all + c.gremlins.all_caught,
      total: acc.total + c.gremlins.total,
    }),
    { book: 0, all: 0, total: 0 },
  );

  return (
    <>
      <h1 className="sr-only">Tiny Python Toybox: little toys, strict rules, sneaky gremlins</h1>
      {moments && star && starBundle && (
        <ToyStage bundle={starBundle} entry={star} generated={moments.generated} python={moments.python} />
      )}

      <section className="toybox" aria-labelledby="toys-h">
        <h2 id="toys-h">The toy box</h2>
        <ul className="toy-grid">
          {toys.map((b) => (
            <li key={b.id} className="toy-tile">
              <Link href={`/chapters/${b.id}/`}>
                <span className="tile-emoji" aria-hidden="true">
                  {b.character.emoji}
                </span>
                <h3>{b.character.name}</h3>
                <p>{b.character.role}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <details className="grownups home-grownups">
        <summary>For grown-ups: the tests are the spec</summary>
        <div className="grownups-body">
          <p>
            These are the programs from Ken Youens-Clark&apos;s <cite>Tiny Python Projects</cite>, a book that teaches
            Python by giving you the tests first. The book&apos;s rules are his test suites, unchanged. I wrote the
            programs from those tests, then added tests for cases real life throws at them.
          </p>
          {totals.total > 0 && (
            <>
              <p>
                The gremlins are mutation testing: each is a copy of a working program with one small change. Across{" "}
                {shown.length} toys, the book&apos;s tests catch{" "}
                <strong>
                  {totals.book} of {totals.total}
                </strong>
                ; with the real-life tests added, they catch{" "}
                <strong>
                  {totals.all} of {totals.total}
                </strong>
                .
              </p>
              <div className="bars">
                <Bar label="The book's tests" value={totals.book} total={totals.total} />
                <Bar label="With real-life tests" value={totals.all} total={totals.total} />
              </div>
            </>
          )}
          <p className="fine">
            {moments && <>Measured by CI on Python {moments.python} ({moments.generated}). </>}
            {parity && (
              <>
                Browsers can&apos;t start processes, so a shim runs each program in-process. CI checks it against
                real processes: {parity.rows.reduce((n, r) => n + r.commands_compared, 0)} commands compared,{" "}
                {parity.mismatches === 0 ? "no differences" : `${parity.mismatches} differences`}.
              </>
            )}
          </p>
        </div>
      </details>
    </>
  );
}

function Bar({ label, value, total }: { label: string; value: number; total: number }) {
  const pct = Math.round((value / total) * 100);
  return (
    <div className="bar">
      <span>{label}</span>
      <span className="bar-track" aria-hidden="true">
        <span className="bar-fill" style={{ display: "block", width: `${pct}%` }} />
      </span>
      <span>{pct}% caught</span>
    </div>
  );
}
