import { API_URL } from "@/lib/config";

type DashboardItem = {
  id: number;
  title: string;
  trend_score: number;
};

type DashboardData = {
  summary: {
    total_anime: number;
    average_trend: number;
  };
  rising: DashboardItem[];
  stable: DashboardItem[];
  cooling: DashboardItem[];
};

export default async function DashboardPage() {
  const data: DashboardData = await fetch(
    `${API_URL}/maple/dashboard/`,
    { cache: "no-store" }
  ).then((res) => res.json());

  return (
    <main className="min-h-screen bg-[#120d1c] p-10 text-white">
      <h1 className="text-3xl font-black">🧠 Maple Intelligence Dashboard</h1>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="rounded-xl bg-white/5 p-4">
          <p className="text-purple-300">Total Anime</p>
          <p className="text-2xl font-bold">{data.summary.total_anime}</p>
        </div>

        <div className="rounded-xl bg-white/5 p-4">
          <p className="text-purple-300">Avg Trend</p>
          <p className="text-2xl font-bold">{data.summary.average_trend}</p>
        </div>
      </div>

      <Section title="🔥 Rising" items={data.rising} />
      <Section title="📊 Stable" items={data.stable} />
      <Section title="❄️ Cooling" items={data.cooling} />
    </main>
  );
}

function Section({
  title,
  items,
}: {
  title: string;
  items: DashboardItem[];
}) {
  return (
    <div className="mt-10">
      <h2 className="text-xl font-bold">{title}</h2>

      <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-3">
        {items.map((a) => (
          <div
            key={a.id}
            className="rounded-xl border border-white/10 bg-white/5 p-3"
          >
            <p className="font-bold">{a.title}</p>
            <p className="text-sm text-purple-300">Trend: {a.trend_score}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
