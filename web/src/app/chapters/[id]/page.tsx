import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ToyStage } from "@/components/ToyStage";
import { BOOK } from "@/data/book";
import { builtChapters, loadBundle, loadMoments } from "@/lib/data";

export const dynamicParams = false;

export function generateStaticParams() {
  return builtChapters().map((id) => ({ id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const b = loadBundle(id);
  return b
    ? { title: `${b.character.name}, ${b.character.role}`, description: b.tagline }
    : { title: "Toy" };
}

export default async function ChapterPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const bundle = loadBundle(id);
  const moments = loadMoments();
  const entry = moments?.chapters.find((c) => c.id === id);
  const ch = BOOK.find((c) => c.id === id);
  if (!bundle || !ch || !moments || !entry) notFound();
  const built = new Set(builtChapters());
  const order = BOOK.filter((c) => built.has(c.id));
  const next = order[order.indexOf(ch) + 1];
  const nextBundle = next ? loadBundle(next.id) : null;

  return (
    <div className="chapter">
      <p className="ch-crumb">
        <Link href="/">All toys</Link> · toy {order.indexOf(ch) + 1} of {order.length}
      </p>
      <ToyStage bundle={bundle} entry={entry} generated={moments.generated} python={moments.python} headingLevel={1} />
      {next && nextBundle && (
        <p className="ch-next">
          <Link href={`/chapters/${next.id}/`}>
            Next toy: {nextBundle.character.emoji} {nextBundle.character.name}
          </Link>
        </p>
      )}
    </div>
  );
}
