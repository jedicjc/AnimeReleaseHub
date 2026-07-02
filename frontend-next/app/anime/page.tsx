import Link from "next/link";
import { AnimeGrid } from "@/components/AnimeGrid";
import { getAnime } from "@/lib/api";

export default async function AnimePage() {
  const anime = await getAnime();

  return (
    <main className="min-h-screen bg-[#120d1c] text-white">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-black">
              🍁 Anime Library
            </h1>

            <p className="mt-3 text-purple-200">
              Maple is currently tracking {anime.length} anime.
            </p>
          </div>

          <Link
            href="/"
            className="rounded-xl bg-pink-500 px-5 py-3 font-bold"
          >
            Dashboard
          </Link>
        </div>

        <AnimeGrid anime={anime} />
      </section>
    </main>
  );
}