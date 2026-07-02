import { ActivitySummary } from "@/components/ActivitySummary";
import { DailyBrief } from "@/components/DailyBrief";
import { MaplePanel } from "@/components/MaplePanel";
import { Navbar } from "@/components/Navbar";
import { NewsGrid } from "@/components/NewsGrid";
import { SearchBar } from "@/components/SearchBar";
import { StatsCards } from "@/components/StatsCards";
import { TrendingNow } from "@/components/TrendingNow";
import { getDashboard, getTrending } from "@/lib/api";

function getGreeting() {
  const hour = new Date().getHours();

  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default async function Home() {
  const dashboard = await getDashboard();
  const trending = await getTrending();

  return (
    <main className="min-h-screen bg-[#120d1c] text-white">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <Navbar />

        <section className="mt-10 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_380px]">
          <div className="rounded-[2rem] border border-white/10 bg-white/10 p-8">
            <div className="mb-4 inline-flex rounded-full border border-pink-300/30 bg-pink-300/10 px-4 py-2 text-sm text-pink-100">
              🍁 Maple Command Center
            </div>

            <h1 className="text-4xl font-black md:text-6xl">
              {getGreeting()}, Carter.
            </h1>

            <p className="mt-5 max-w-2xl text-lg leading-8 text-purple-100">
              Maple tracks anime news, builds intelligence signals, and ranks
              what matters right now.
            </p>

            <SearchBar />

            <DailyBrief dashboard={dashboard} />
          </div>

          <MaplePanel />
        </section>

        <StatsCards
          newsCount={dashboard.news_count}
          animeCount={dashboard.anime_count}
          dubCount={dashboard.dub_count}
        />

        <ActivitySummary categoryCounts={dashboard.category_counts} />

        <TrendingNow anime={trending} />

        <NewsGrid articles={dashboard.latest_news} />
      </section>
    </main>
  );
}