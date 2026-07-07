import Link from "next/link";
import type { Anime } from "@/lib/api";
import { getAnimeDisplayTitle } from "@/lib/anime";

export function UpcomingSection({ anime }: { anime: Anime[] }) {
  if (!anime.length) return null;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-black">📅 Upcoming Releases</h2>

      <div className="mt-5 space-y-3">
        {anime.slice(0, 6).map((item) => (
          <Link
            key={item.id}
            href={`/anime/${item.id}`}
            className="block rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:bg-white/10"
          >
            <h3 className="font-black text-white">
              {getAnimeDisplayTitle(item)}
            </h3>

            <p className="mt-2 text-sm text-purple-300">
              {item.release_season || item.release_year
                ? `${item.release_season ?? ""} ${item.release_year ?? ""}`.trim()
                : "Release unknown"}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
