import Link from "next/link";
import { AnimePoster } from "@/components/AnimePoster";
import { StatusBadge } from "@/components/StatusBadge";
import { getAnimeById } from "@/lib/api";

type Props = {
  params: Promise<{
    id: string;
  }>;
};

export default async function AnimeDetailPage({ params }: Props) {
  const { id } = await params;
  const anime = await getAnimeById(id);

  if (!anime) {
    return (
      <main className="min-h-screen bg-[#120d1c] text-white">
        <section className="mx-auto max-w-4xl px-6 py-10">
          <h1 className="text-4xl font-black">Anime not found</h1>

          <Link href="/anime" className="mt-6 inline-block text-pink-300">
            ← Back to Anime Library
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#120d1c] text-white">
      <section className="mx-auto max-w-6xl px-6 py-10">
        <Link href="/anime" className="text-pink-300">
          ← Back to Anime Library
        </Link>

        <div className="mt-8 grid gap-8 rounded-[2rem] border border-white/10 bg-white/10 p-8 lg:grid-cols-[320px_1fr]">
          <AnimePoster title={anime.title} posterUrl={anime.poster_url} />

          <div>
            <StatusBadge status={anime.status ?? "unknown"} />

            <h1 className="mt-5 text-5xl font-black">{anime.title}</h1>

            <div className="mt-8 grid gap-4 md:grid-cols-2">
              <Info label="English Dub" value={anime.english_dub_status ?? "Unknown"} />
              <Info label="Streaming" value={anime.streaming_platform ?? "Unknown"} />
              <Info label="Release Season" value={anime.release_season ?? "Unknown"} />
              <Info label="Release Year" value={anime.release_year?.toString() ?? "Unknown"} />
              <Info label="Score" value={anime.score?.toString() ?? "Unknown"} />
              <Info label="Genres" value={anime.genres ?? "Unknown"} />
            </div>

            {anime.synopsis && (
              <div className="mt-8 rounded-3xl bg-black/20 p-5">
                <p className="text-sm text-purple-200">Synopsis</p>
                <p className="mt-2 leading-relaxed text-purple-100">
                  {anime.synopsis}
                </p>
              </div>
            )}

            {anime.notes && (
              <div className="mt-8 rounded-3xl bg-black/20 p-5">
                <p className="text-sm text-purple-200">Maple Notes</p>
                <p className="mt-2 text-purple-100">{anime.notes}</p>
              </div>
            )}

            {anime.source_url && (
              <a
                href={anime.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-8 inline-block rounded-xl bg-pink-500 px-5 py-3 font-bold"
              >
                View Original Announcement
              </a>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl bg-black/20 p-5">
      <p className="text-sm text-purple-200">{label}</p>
      <p className="mt-2 text-lg font-bold">{value}</p>
    </div>
  );
}