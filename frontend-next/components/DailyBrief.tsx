import { DashboardData } from "@/types/dashboard";

type Props = {
  dashboard: DashboardData;
};

export function DailyBrief({ dashboard }: Props) {
  const topHeadlines = dashboard.latest_news.slice(0, 3);

  return (
    <div className="mt-6 rounded-3xl border border-pink-300/20 bg-pink-300/10 p-5">
      <p className="text-sm font-bold text-pink-100">🍁 Maple Daily Brief</p>

      <p className="mt-3 text-purple-100">
        I scanned the latest anime news and found{" "}
        <strong>{dashboard.news_count}</strong> articles,{" "}
        <strong>{dashboard.anime_count}</strong> tracked anime, and{" "}
        <strong>{dashboard.dub_count}</strong> dub updates.
      </p>

      {topHeadlines.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-bold text-pink-100">Highlights</p>

          <ul className="mt-2 space-y-2 text-sm text-purple-100">
            {topHeadlines.map((article) => (
              <li key={article.id}>• {article.title}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}