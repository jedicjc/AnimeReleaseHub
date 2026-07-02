"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { motion } from "framer-motion";

import type { Anime } from "@/lib/api";
import { AnimePoster } from "@/components/AnimePoster";
import { StatusBadge } from "@/components/StatusBadge";

type Props = {
  anime: Anime[];
};

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
    },
  },
};

const cardVariants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  show: {
    opacity: 1,
    y: 0,
  },
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
          className="w-full rounded-2xl border border-white/10 bg-black/20 px-5 py-4 text-white placeholder-purple-300 outline-none transition focus:border-pink-400"
        />
      </div>

      <motion.div
        className="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {filteredAnime.map((item) => (
          <motion.div
            key={item.id}
            variants={cardVariants}
            transition={{ duration: 0.35 }}
          >
            <Link
              href={`/anime/${item.id}`}
              className="group relative block overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-b from-white/10 to-black/30 shadow-lg transition-all duration-300 hover:-translate-y-2 hover:border-pink-300/40 hover:shadow-pink-500/10"
            >
              <AnimePoster
                title={item.title}
                posterUrl={item.poster_url}
              />

              <div className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <StatusBadge status={item.status} />

                  <span className="text-sm text-purple-300 transition group-hover:text-pink-200">
                    View →
                  </span>
                </div>

                <h2 className="mt-5 text-2xl font-black leading-tight">
                  {item.title}
                </h2>

                <div className="mt-5 space-y-3 text-sm text-purple-100">
                  <p>
                    🎙️ Dub:{" "}
                    <span className="font-semibold">
                      {item.english_dub_status}
                    </span>
                  </p>

                  <p>
                    📅 Release:{" "}
                    <span className="font-semibold">
                      {item.release_season || item.release_year
                        ? `${item.release_season ?? ""} ${item.release_year ?? ""}`.trim()
                        : "Unknown"}
                    </span>
                  </p>

                  <p>
                    📺 Platform:{" "}
                    <span className="font-semibold">
                      {item.streaming_platform ?? "Unknown"}
                    </span>
                  </p>
                </div>

                <div className="mt-6 h-px bg-white/10" />

                <p className="mt-4 text-sm text-purple-300">
                  Maple Intelligence detected this title from trusted anime
                  news signals.
                </p>
              </div>
            </Link>
          </motion.div>
        ))}

        {filteredAnime.length === 0 && (
          <motion.div
            variants={cardVariants}
            className="col-span-full rounded-3xl border border-white/10 bg-white/10 p-10 text-center"
          >
            <h2 className="text-2xl font-bold">
              No anime found
            </h2>

            <p className="mt-3 text-purple-300">
              Try searching for another title.
            </p>
          </motion.div>
        )}
      </motion.div>
    </>
  );
}