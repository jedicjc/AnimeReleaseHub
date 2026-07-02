import Link from "next/link";
import { AnimeGrid } from "@/components/AnimeGrid";
import { FeaturedAnime } from "@/components/FeaturedAnime";
import { Navbar } from "@/components/Navbar";
import { getAnime } from "@/lib/api";

export default async function AnimePage() {
  const anime = await getAnime();

  return (
    <main className="min-h-screen bg-[#120d1c] text-white">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <Navbar />

        <div className="mt-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-widest text-pink-300">
              Maple Library
            </p>

            <h1 className="mt-2 text-5xl font-black">
              Anime Library
            </h1>

            <p className="mt-4 text-lg text-purple-200">
              Maple is currently tracking{" "}
              <span className="font-bold text-white">
                {anime.length}
              </span>{" "}
              anime titles.
            </p>
          </div>

          <Link
            href="/"
            className="rounded-xl border border-pink-300/30 bg-pink-500/20 px-6 py-3 font-bold transition hover:bg-pink-500/30"
          >
            ← Dashboard
          </Link>
        </div>

        {anime.length > 0 && (
          <div className="mt-10">
            <FeaturedAnime anime={anime[0]} />
          </div>
        )}

        <div className="mt-10">
          <AnimeGrid anime={anime} />
        </div>
      </section>
    </main>
  );
}