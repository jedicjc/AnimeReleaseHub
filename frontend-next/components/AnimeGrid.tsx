"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Anime } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

type Props = {
  anime: Anime[];
};

export function AnimeGrid({ anime }: Props) {
  const [query, setQuery] = useState("");

  const filteredAnime = useMemo(() => {
    const search = query.toLowerCase().trim();

    if (!search) return anime;

    return anime.filter((item) =>
      item.title.toLowerCase().includes(search)
    );
  }, [anime, query]);

  return (
    <>
      <div className="mt-8">
        <input
          type="text"
          placeholder="🔍 Search your anime library..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-2xl border border-white/10 bg-black/20 px-5 py-4 text-white placeholder-purple-300 outline-none focus:border-pink-400"
        />
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {filteredAnime.map((item) => (
          <Link
            key={item.id}
            href={`/anime/${item.id}`}
            className="block rounded-3xl border border-white/10 bg-white/10 p-6 transition hover:bg-white/15"
          >
            <h2 className="text-xl font-bold">{item.title}</h2>

            <div className="mt-4">
              <StatusBadge status={item.status} />
            </div>

            <p className="mt-4 text-sm text-purple-200">
              Dub: {item.english_dub_status}
            </p>

            {item.source_url && (
              <p className="mt-5 text-pink-300">
                View Details →
              </p>
            )}
          </Link>
        ))}

        {filteredAnime.length === 0 && (
          <div className="col-span-full rounded-3xl border border-white/10 bg-white/10 p-8 text-center">
            <h2 className="text-2xl font-bold">No anime found</h2>

            <p className="mt-3 text-purple-300">
              Try a different search term.
            </p>
          </div>
        )}
      </div>
    </>
  );
}