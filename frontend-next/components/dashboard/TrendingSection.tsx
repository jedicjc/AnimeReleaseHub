import Image from "next/image";
import Link from "next/link";
import type { Anime } from "@/lib/api";
import { getAnimeDisplayTitle } from "@/lib/anime";

function getTrendBadge(score?: number | null) {
  const value = score ?? 0;

  if (value >= 80) return "Exploding";
  if (value >= 60) return "Hot";
  if (value >= 40) return "Rising";
  if (value >= 20) return "Watchlist";
  return "New";
}

export function TrendingSection({ anime }: { anime: Anime[] }) {
  if (!anime.length) return null;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-black">Trending Now</h2>

        <Link
          href="/anime"
          className="shrink-0 text-sm font-bold text-pink-300 transition hover:text-pink-200"
        >
          View all
        </Link>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
        {anime.slice(0, 6).map((item, index) => {
          const displayTitle = getAnimeDisplayTitle(item);

          return (
            <Link
              key={item.id}
              href={`/anime/${item.id}`}
              className="group overflow-hidden rounded-2xl border border-white/10 bg-black/20 transition-all duration-300 hover:-translate-y-2 hover:border-pink-500/30 hover:shadow-2xl hover:shadow-pink-500/20"
            >
              <div className="relative overflow-hidden rounded-t-2xl">
                {item.poster_url ? (
                  <Image
                    src={item.poster_url}
                    alt={displayTitle}
                    width={500}
                    height={750}
                    className="aspect-[2/3] w-full object-cover transition-all duration-500 group-hover:scale-105"
                  />
                ) : (
                  <div className="flex aspect-[2/3] w-full items-center justify-center rounded-t-2xl bg-pink-500/10 text-5xl">
                    M
                  </div>
                )}

                <div className="absolute left-3 top-3 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-yellow-400 via-orange-500 to-pink-600 shadow-xl ring-4 ring-black/40">
                  <span className="text-lg font-black text-white">
                    {index + 1}
                  </span>
                </div>
              </div>

              <div className="p-4">
                <div className="inline-flex items-center gap-2 rounded-full bg-orange-500/20 px-3 py-1 text-xs font-bold text-orange-300">
                  <span>{getTrendBadge(item.trend_score)}</span>
                  <span className="text-white">
                    {item.trend_score?.toFixed(1) ?? "0.0"}
                  </span>
                </div>

                <h3 className="mt-3 line-clamp-2 min-h-[3rem] font-black text-white">
                  {displayTitle}
                </h3>

                {item.genres && (
                  <p className="mt-2 line-clamp-1 text-xs text-purple-300">
                    {item.genres}
                  </p>
                )}

                <div className="mt-4 rounded-xl bg-pink-500/10 p-3">
                  <p className="text-xs uppercase tracking-widest text-pink-300">
                    Maple Score
                  </p>

                  <p className="text-2xl font-black text-white">
                    {item.maple_score?.toFixed(1) ?? "N/A"}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
