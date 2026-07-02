import Link from "next/link";
import type { Anime } from "@/lib/api";
import { AnimePoster } from "@/components/AnimePoster";
import { StatusBadge } from "@/components/StatusBadge";

type Props = {
  anime: Anime;
};

export function FeaturedAnime({ anime }: Props) {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-pink-300/20 bg-gradient-to-br from-pink-500/10 via-purple-500/10 to-blue-500/10 p-8 shadow-2xl shadow-pink-500/10">

      {/* Glow background */}
      <div className="absolute inset-0 animate-pulse bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 opacity-20 blur-3xl" />

      <div className="relative z-10 grid gap-8 lg:grid-cols-[280px_1fr]">
        <AnimePoster title={anime.title} posterUrl={anime.poster_url} />

        <div>
          <p className="text-sm font-bold uppercase tracking-widest text-pink-300">
            🍁 Featured Anime
          </p>

          <div className="mt-3">
            <StatusBadge status={anime.status} />
          </div>

          <h1 className="mt-5 text-4xl font-black lg:text-5xl">
            {anime.title}
          </h1>

          {anime.synopsis && (
            <p className="mt-5 text-purple-100 line-clamp-4">
              {anime.synopsis}
            </p>
          )}

          <div className="mt-8 grid gap-4 sm:grid-cols-2 text-sm">
            <Info label="Dub" value={anime.english_dub_status} />
            <Info label="Release" value={`${anime.release_season ?? ""} ${anime.release_year ?? ""}`} />
            <Info label="Platform" value={anime.streaming_platform ?? "Unknown"} />
            <Info label="Score" value={anime.score?.toString() ?? "Unknown"} />
          </div>

          <Link
            href={`/anime/${anime.id}`}
            className="mt-8 inline-flex rounded-xl bg-pink-500 px-6 py-3 font-bold hover:bg-pink-400"
          >
            View Details →
          </Link>
        </div>
      </div>
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-black/20 p-4">
      <p className="text-xs text-purple-300">{label}</p>
      <p className="mt-1 font-bold">{value}</p>
    </div>
  );
}