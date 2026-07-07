import Image from "next/image";
import { Navbar } from "@/components/Navbar";
import { SearchBar } from "@/components/SearchBar";
import { TrendingSection } from "@/components/dashboard/TrendingSection";
import { MaplePicksSection } from "@/components/dashboard/MaplePicksSection";
import { MapleInsight } from "@/components/dashboard/MapleInsight";
import { SectionReveal } from "@/components/dashboard/SectionReveal";
import { HighestRatedSection } from "@/components/dashboard/HighestRatedSection";
import { LatestNewsSection } from "@/components/dashboard/LatestNewsSection";
import { UpcomingSection } from "@/components/dashboard/UpcomingSection";
import { getDashboard } from "@/lib/api";

export default async function HomePage() {
  const dashboard = await getDashboard();
  const heroStats = [
    { label: "Anime", value: dashboard.stats.anime, icon: "🍿" },
    { label: "News", value: dashboard.stats.news, icon: "📰" },
    { label: "Trending", value: dashboard.stats.trending, icon: "🔥" },
    { label: "Picks", value: dashboard.stats.maple_picks, icon: "🍁" },
  ];

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#120d1c] text-white">
      <div className="premium-blob pointer-events-none absolute -left-32 top-20 h-96 w-96 rounded-full bg-purple-600/25 blur-[150px]" />
      <div className="premium-blob-slow pointer-events-none absolute right-0 top-48 h-96 w-96 rounded-full bg-pink-500/25 blur-[150px]" />
      <div className="premium-blob pointer-events-none absolute bottom-40 left-1/3 h-80 w-80 rounded-full bg-cyan-500/20 blur-[150px]" />

      <section className="relative mx-auto max-w-7xl px-6 py-8">
        <Navbar />

        <section className="mt-10 grid items-center gap-10 lg:grid-cols-2">
          <div className="rounded-3xl border border-pink-300/20 bg-white/5 p-8 backdrop-blur">
            <p className="text-sm uppercase tracking-widest text-pink-300">
              🍁 Maple Intelligence
            </p>

            <h1 className="mt-4 text-5xl font-black leading-tight md:text-7xl">
              Hi! I&apos;m Maple.
            </h1>

            <p className="mt-6 max-w-xl text-lg text-purple-200">
              I&apos;ve analyzed today&apos;s anime announcements, trend scores,
              community ratings, and release schedules. Here&apos;s everything
              you shouldn&apos;t miss.
            </p>

            <div className="mt-8 max-w-xl">
              <SearchBar />
            </div>
          </div>

          <div className="relative flex justify-center">
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-pink-500/30 via-purple-500/20 to-cyan-500/20 blur-[120px]" />

            <Image
              src="/images/maple.png"
              alt="Maple anime intelligence assistant"
              width={520}
              height={520}
              priority
              className="maple-float relative z-10 drop-shadow-2xl"
            />
          </div>
        </section>

        <section className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {heroStats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-white/10 bg-black/20 p-4 transition-all duration-300 hover:-translate-y-1 hover:border-pink-300/30 hover:bg-white/10 hover:shadow-xl hover:shadow-pink-500/10"
            >
              <p className="text-sm font-bold text-purple-300">
                {stat.icon} {stat.label}
              </p>

              <p className="mt-2 text-3xl font-black text-white">
                {stat.value}
              </p>
            </div>
          ))}
        </section>

        <div className="mt-12 space-y-8">
          <SectionReveal>
            <MapleInsight insight={dashboard.insight} />
          </SectionReveal>

          <SectionReveal delay={80}>
            <TrendingSection anime={dashboard.trending} />
          </SectionReveal>

          <SectionReveal delay={120}>
            <MaplePicksSection anime={dashboard.maple_picks} />
          </SectionReveal>

          <SectionReveal delay={160}>
            <div className="grid gap-8 lg:grid-cols-2">
              <HighestRatedSection anime={dashboard.highest_rated} />
              <UpcomingSection anime={dashboard.upcoming} />
            </div>
          </SectionReveal>

          <SectionReveal delay={200}>
            <LatestNewsSection news={dashboard.latest_news} />
          </SectionReveal>
        </div>
      </section>
    </main>
  );
}
