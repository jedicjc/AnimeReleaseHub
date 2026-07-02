import Link from "next/link";

type Anime = {
  id: number;
  title: string;
  trend_score: number;
  movement?: string;
  spike_label?: string;
  insight?: string;
};

type Props = {
  anime: Anime[];
};

function getBarPercent(score: number) {
  const max = 150;
  return Math.min(Math.max((score / max) * 100, 0), 100);
}

export function TrendingNow({ anime }: Props) {
  return (
    <section className="mt-10 rounded-[2rem] border border-white/10 bg-white/5 p-8">
      <h2 className="text-2xl font-black">🔥 Trending Now</h2>

      <p className="mt-2 text-sm text-purple-300">
        Maple Spike Detection System — live momentum tracking
      </p>

      <div className="mt-6 space-y-4">
        {anime.map((item, index) => {
          const percent = getBarPercent(item.trend_score);

          return (
            <Link
              key={item.id}
              href={`/anime/${item.id}`}
              className="block rounded-2xl border border-white/10 bg-gradient-to-b from-black/40 to-black/20 p-5 transition-all hover:-translate-y-1 hover:border-pink-300/30 hover:shadow-lg hover:shadow-pink-500/10"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="font-bold">
                  #{index + 1} {item.title}
                </div>

                <div className="text-xs text-purple-300">
                  {item.spike_label ?? "➖ Stable Interest"}
                </div>
              </div>

              <div className="mt-4">
                <div className="h-3 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-pink-400 shadow-[0_0_12px_rgba(244,114,182,0.55)]"
                    style={{ width: `${percent}%` }}
                  />
                </div>

                <div className="mt-2 text-xs text-purple-300">
                  Hype Score: {item.trend_score.toFixed(0)}
                </div>
              </div>

              {item.insight && (
                <p className="mt-3 text-xs leading-relaxed text-purple-300">
                  {item.insight}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </section>
  );
}