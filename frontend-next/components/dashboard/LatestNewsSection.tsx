import type { AnimeNews } from "@/lib/api";

function getCategoryIcon(category: string) {
  const value = category.toLowerCase();

  if (value.includes("trailer")) return "🎬";
  if (value.includes("cast")) return "👥";
  if (value.includes("visual")) return "🎨";
  if (value.includes("sequel")) return "📺";
  if (value.includes("announcement")) return "📢";
  if (value.includes("delay")) return "⏰";
  if (value.includes("dub")) return "🌍";
  return "📰";
}

function formatCategory(category: string) {
  return category
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function LatestNewsSection({ news }: { news: AnimeNews[] }) {
  if (!news.length) return null;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
      <h2 className="text-xl font-black">📰 Latest News</h2>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {news.slice(0, 6).map((item) => (
          <a
            key={item.id}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="group block rounded-2xl border border-white/10 bg-black/20 p-4 transition-all duration-300 hover:-translate-y-1 hover:border-pink-500/30 hover:bg-white/10 hover:shadow-xl hover:shadow-pink-500/10"
          >
            <p className="text-sm font-black text-pink-300">
              {getCategoryIcon(item.category)} {formatCategory(item.category)}
            </p>

            <h3 className="mt-3 font-bold leading-snug text-white">
              {item.title}
            </h3>

            <div className="mt-4 flex items-center justify-between gap-4 text-xs font-bold text-purple-300">
              <span>{item.source}</span>
              <span className="text-pink-300 transition group-hover:text-pink-200">
                Read →
              </span>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
