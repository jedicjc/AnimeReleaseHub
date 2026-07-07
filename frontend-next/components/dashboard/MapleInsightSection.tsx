import type { Anime } from "@/lib/api";

function mostCommonGenre(anime: Anime[]) {
  const counts = new Map<string, number>();

  for (const item of anime) {
    for (const genre of item.genres?.split(",") ?? []) {
      const trimmed = genre.trim();

      if (trimmed) {
        counts.set(trimmed, (counts.get(trimmed) ?? 0) + 1);
      }
    }
  }

  return [...counts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
}

export function MapleInsightSection({
  trending,
  maplePicks,
}: {
  trending: Anime[];
  maplePicks: Anime[];
}) {
  const leadingGenre = mostCommonGenre([...trending, ...maplePicks]);
  const topPick = maplePicks[0] ?? trending[0];
  const secondGenre = [...new Set(
    [...trending, ...maplePicks]
      .flatMap((item) => item.genres?.split(",") ?? [])
      .map((genre) => genre.trim())
      .filter(Boolean),
  )].find((genre) => genre !== leadingGenre);
  const sportsRising = [...trending, ...maplePicks].some((item) =>
    item.genres?.toLowerCase().includes("sports"),
  );

  if (!topPick) return null;

  return (
    <section className="rounded-3xl border border-pink-300/20 bg-black/20 p-6">
      <p className="text-sm font-black uppercase tracking-widest text-pink-300">
        🍁 Today&apos;s Insight
      </p>

      <p className="mt-3 max-w-4xl text-lg leading-8 text-purple-100">
        {leadingGenre && secondGenre
          ? `${leadingGenre} and ${secondGenre} continue to dominate this week's announcements.`
          : leadingGenre
            ? `${leadingGenre} continues to dominate this week's announcements.`
            : "This week's anime announcements are moving quickly across Maple's dashboard."}
      </p>

      <p className="mt-4 max-w-4xl text-lg leading-8 text-purple-100">
        {topPick.title} remains Maple&apos;s highest recommendation due to its{" "}
        {(topPick.score ?? 0) >= 8
          ? "excellent community rating"
          : "solid community signals"}{" "}
        and{" "}
        {(topPick.trend_score ?? 0) >= 60
          ? "strong trend momentum."
          : "steady trend momentum."}{" "}
        {sportsRising ? "Sports anime are also showing a surprising lift." : ""}
      </p>
    </section>
  );
}
