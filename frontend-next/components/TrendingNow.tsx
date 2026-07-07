"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API_URL } from "@/lib/config";
import { getAnimeDisplayTitle } from "@/lib/anime";

type Anime = {
  id: number;
  title: string;
  title_english?: string | null;
  trend_score: number;
  movement?: string;
  spike_label?: string;
  insight?: string;
};

export function TrendingNow({ anime: initialData }: { anime: Anime[] }) {
  const [anime, setAnime] = useState(initialData);
  const [loading, setLoading] = useState(false);

  async function fetchTrending() {
    try {
      setLoading(true);

      const res = await fetch(`${API_URL}/trending/`, {
        cache: "no-store",
      });

      const data = await res.json();
      setAnime(data);
    } catch (err) {
      console.error("Failed to refresh trending", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      fetchTrending();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, []);

  function getBarPercent(score: number) {
    const max = 150;
    return Math.min(Math.max((score / max) * 100, 0), 100);
  }

  return (
    <section className="mt-10 rounded-[2rem] border border-white/10 bg-white/5 p-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-black">🔥 Trending Now</h2>

        {loading && (
          <span className="text-xs text-purple-300 animate-pulse">
            updating...
          </span>
        )}
      </div>

      <p className="mt-2 text-sm text-purple-300">
        Live Maple Intelligence Feed — updates every 30s
      </p>

      <div className="mt-6 space-y-4">
        {anime.map((item, index) => (
          <Link
            key={item.id}
            href={`/anime/${item.id}`}
            className="block rounded-2xl border border-white/10 bg-gradient-to-b from-black/40 to-black/20 p-5 transition hover:border-pink-300/30 hover:shadow-lg hover:shadow-pink-500/10"
          >
            <div className="flex items-center justify-between">
              <div className="font-bold">
                #{index + 1} {getAnimeDisplayTitle(item)}
              </div>

              <div className="text-xs text-purple-300">
                {item.spike_label ?? "➖ Stable"}
              </div>
            </div>

            <div className="mt-4">
              <div className="h-3 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-pink-400 shadow-[0_0_12px_rgba(244,114,182,0.55)] transition-all duration-700"
                  style={{
                    width: `${getBarPercent(item.trend_score)}%`,
                  }}
                />
              </div>

              <div className="mt-2 text-xs text-purple-300">
                Hype Score: {item.trend_score.toFixed(0)}
              </div>
            </div>

            {item.insight && (
              <p className="mt-3 text-xs text-purple-300">
                {item.insight}
              </p>
            )}
          </Link>
        ))}
      </div>
    </section>
  );
}
