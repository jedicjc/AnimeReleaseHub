import { notFound } from "next/navigation";

import { getAnimeById } from "@/lib/api";
import { AnimePoster } from "@/components/AnimePoster";
import { Navbar } from "@/components/Navbar";
import { StatusBadge } from "@/components/StatusBadge";
import { API_URL } from "@/lib/config";

type Props = {
  params: Promise<{
    id: string;
  }>;
};

type MapleResponse = {
  hype_score?: number;
  audience?: string;
  insight?: string;
};

type ExplanationResponse = {
  id: number;
  title: string;
  explanation: string[];
};

type Recommendation = {
  id: number;
  title: string;
  score: number;
  why?: string[];
};

export default async function AnimeDetailPage({ params }: Props) {
  const { id } = await params;
  const anime = await getAnimeById(id);

  if (!anime?.id) {
    notFound();
  }

  const data = {
    title: anime.title ?? "Unknown Anime",
    poster_url: anime.poster_url ?? null,
    status: anime.status ?? "unknown",
    synopsis: anime.synopsis ?? "No synopsis available.",
    dub: anime.english_dub_status ?? "Unknown",
    release:
      anime.release_season || anime.release_year
        ? `${anime.release_season ?? ""} ${anime.release_year ?? ""}`.trim()
        : "Unknown",
    platform: anime.streaming_platform ?? "Unknown",
    score: anime.score ?? "N/A",
    genres: anime.genres ?? null,
  };

  let maple: MapleResponse | null = null;

  try {
    const res = await fetch(`${API_URL}/maple/anime/${id}`, {
      cache: "no-store",
    });

    if (res.ok) {
      const json = await res.json();
      if (json?.hype_score !== undefined) {
        maple = json;
      }
    }
  } catch {
    maple = null;
  }

  let explain: ExplanationResponse | null = null;

  try {
    const res = await fetch(`${API_URL}/maple/explain/${id}`, {
      cache: "no-store",
    });

    if (res.ok) {
      explain = await res.json();
    }
  } catch {
    explain = null;
  }

  let recs: Recommendation[] = [];

  try {
    const res = await fetch(`${API_URL}/recommendations/${id}`, {
      cache: "no-store",
    });

    if (res.ok) {
      recs = await res.json();
    }
  } catch {
    recs = [];
  }

  return (
    <main className="min-h-screen bg-[#120d1c] text-white">
      <section className="mx-auto max-w-5xl px-6 py-10">
        <Navbar />

        <div className="mt-10 grid gap-10 lg:grid-cols-[300px_1fr]">
          <div>
            <AnimePoster title={data.title} posterUrl={data.poster_url} />
          </div>

          <div>
            <StatusBadge status={data.status} />

            <h1 className="mt-4 text-4xl font-black">{data.title}</h1>

            <p className="mt-5 leading-relaxed text-purple-200">
              {data.synopsis}
            </p>

            <div className="mt-6 space-y-2 text-sm text-purple-300">
              <p>
                Dub:{" "}
                <span className="font-semibold text-white">{data.dub}</span>
              </p>

              <p>
                Release:{" "}
                <span className="font-semibold text-white">{data.release}</span>
              </p>

              <p>
                Platform:{" "}
                <span className="font-semibold text-white">
                  {data.platform}
                </span>
              </p>

              <p>
                Score:{" "}
                <span className="font-semibold text-white">{data.score}</span>
              </p>

              {data.genres && (
                <p>
                  Genres:{" "}
                  <span className="font-semibold text-white">
                    {data.genres}
                  </span>
                </p>
              )}
            </div>
          </div>
        </div>

        {maple?.hype_score !== undefined ? (
          <section className="mt-12 rounded-3xl border border-pink-300/20 bg-white/5 p-6">
            <h2 className="text-xl font-black">Maple Intelligence</h2>

            <div className="mt-5 space-y-4 text-sm text-purple-200">
              <div className="flex justify-between gap-6">
                <span>Hype Score</span>
                <span className="font-bold text-white">
                  {maple.hype_score}/100
                </span>
              </div>

              <div className="flex justify-between gap-6">
                <span>Audience</span>
                <span className="font-bold text-white">
                  {maple.audience ?? "Unknown"}
                </span>
              </div>

              <div className="h-px bg-white/10" />

              <p className="text-purple-300">
                {maple.insight ?? "No analysis available yet."}
              </p>
            </div>
          </section>
        ) : (
          <div className="mt-12 rounded-3xl border border-white/10 bg-white/5 p-6 text-purple-300">
            Maple Intelligence loading...
          </div>
        )}

        {(explain?.explanation?.length ?? 0) > 0 && (
          <section className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-6">
            <h2 className="text-xl font-black text-white">
              Why this anime matters
            </h2>

            <ul className="mt-4 space-y-2 text-sm text-purple-200">
              {explain?.explanation.map((item, i) => (
                <li key={i} className="flex gap-2">
                  <span>*</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {recs?.length > 0 && (
          <section className="mt-12">
            <h2 className="text-xl font-black text-white">Similar Anime</h2>

            <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3">
              {recs.map((a) => (
                <a
                  key={a.id}
                  href={`/anime/${a.id}`}
                  className="rounded-xl border border-white/10 bg-white/5 p-3 hover:bg-white/10"
                >
                  <p className="text-sm font-bold text-white">{a.title}</p>

                  <p className="text-xs text-purple-300">
                    Score: {a.score}
                  </p>

                  {(a.why?.length ?? 0) > 0 && (
                    <p className="mt-2 text-[10px] text-purple-400">
                      {a.why?.[0]}
                    </p>
                  )}
                </a>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
