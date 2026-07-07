import Link from "next/link";
import type { Anime } from "@/lib/api";
import { getAnimeDisplayTitle } from "@/lib/anime";

export function HighestRatedSection({ anime }: { anime: Anime[] }) {
  if (!anime.length) return null;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-black">⭐ Highest Rated</h2>

      <div className="mt-5 space-y-3">
        {anime.slice(0, 6).map((item, index) => (
          <Link
            key={item.id}
            href={`/anime/${item.id}`}
            className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:bg-white/10"
          >
            <div>
              <p className="text-xs font-bold text-purple-300">
                #{index + 1}
              </p>
              <h3 className="font-black text-white">
                {getAnimeDisplayTitle(item)}
              </h3>
            </div>

            <p className="text-lg font-black text-pink-300">
              {item.score ?? "N/A"}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
