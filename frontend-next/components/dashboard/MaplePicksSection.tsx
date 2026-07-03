import Link from "next/link";
import type { Anime } from "@/lib/api";

function explainPick(anime: Anime) {
  if ((anime.trend_score ?? 0) >= 60) {
    return "Strong trend momentum makes this one of Maple's top picks.";
  }

  if ((anime.score ?? 0) >= 8) {
    return "High community rating makes this a standout recommendation.";
  }

  return "Maple flagged this as a title worth watching.";
}

function calculateDisplayMapleScore(anime: Anime) {
  if (anime.maple_score !== null && anime.maple_score !== undefined) {
    return anime.maple_score;
  }

  const trend = anime.trend_score ?? 0;
  const malScore = anime.score ?? 0;
  const popularity = anime.popularity ?? 999999;
  const favorites = anime.favorites ?? 0;
  const members = anime.members ?? 0;
  const rank = anime.rank ?? 999999;

  let score = 0;

  score += trend * 0.35;
  score += malScore * 4;

  if (popularity < 1000) score += 12;
  else if (popularity < 5000) score += 7;
  else if (popularity < 10000) score += 3;

  if (rank < 500) score += 10;
  else if (rank < 2000) score += 5;

  if (members > 100000) score += 8;
  else if (members > 25000) score += 4;

  if (favorites > 10000) score += 6;
  else if (favorites > 1000) score += 3;

  if (anime.status === "upcoming") score += 8;
  if (anime.trailer_url) score += 4;

  return Math.round(Math.min(score, 99) * 100) / 100;
}

export function MaplePicksSection({ anime }: { anime: Anime[] }) {
  if (!anime.length) return null;

  return (
    <section className="rounded-3xl border border-pink-300/20 bg-pink-500/10 p-6">
      <h2 className="text-xl font-black">🍁 Maple Picks</h2>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {anime.slice(0, 3).map((item) => (
          <Link
            key={item.id}
            href={`/anime/${item.id}`}
            className="rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:bg-white/10"
          >
            <p className="text-xs font-bold text-pink-300">🍁 Maple Pick</p>

            <h3 className="mt-2 font-black text-white">{item.title}</h3>

            <p className="mt-3 text-sm text-purple-200">
              {explainPick(item)}
            </p>

            <div className="mt-4 rounded-2xl border border-pink-300/20 bg-pink-500/10 p-3">
              <p className="text-xs font-bold uppercase tracking-widest text-pink-300">
                🍁 Maple Score
              </p>

              <p className="mt-1 text-3xl font-black text-white">
                {calculateDisplayMapleScore(item)}
              </p>

              <div className="mt-2 flex gap-3 text-xs text-purple-300">
                <span>🔥 Trend {item.trend_score ?? 0}</span>
                <span>⭐ MAL {item.score ?? "N/A"}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
