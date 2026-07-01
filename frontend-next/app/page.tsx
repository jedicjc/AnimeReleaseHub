import Image from "next/image";

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#120d1c] text-white">
      <section className="relative mx-auto grid min-h-screen max-w-7xl grid-cols-1 items-center gap-10 px-6 py-10 lg:grid-cols-2">
        <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-pink-400/20 blur-3xl" />
        <div className="absolute bottom-10 left-10 h-80 w-80 rounded-full bg-purple-500/20 blur-3xl" />

        <div className="relative z-10">
          <div className="mb-6 inline-flex rounded-full border border-pink-300/30 bg-pink-300/10 px-4 py-2 text-sm text-pink-100">
            🍁 Powered by MapleOS
          </div>

          <h1 className="max-w-3xl text-5xl font-black leading-tight tracking-tight md:text-7xl">
            All announced anime. All English dubs. One hub.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-purple-100">
            Hi, I’m Maple — your anime release assistant. I track upcoming anime,
            release dates, English dubs, trailers, and trusted news updates so
            you don’t have to.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <button className="rounded-full bg-pink-300 px-6 py-3 font-bold text-purple-950 shadow-lg shadow-pink-400/20">
              Explore Anime
            </button>
            <button className="rounded-full border border-white/20 bg-white/10 px-6 py-3 font-bold text-white">
              View Dub Tracker
            </button>
          </div>

          <div className="mt-12 grid max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5">
              <p className="text-sm text-purple-200">Latest News</p>
              <p className="mt-2 text-3xl font-black">10</p>
              <p className="mt-2 text-sm text-purple-100">
                Fresh headlines from Maple Scout.
              </p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/10 p-5">
              <p className="text-sm text-purple-200">Upcoming Anime</p>
              <p className="mt-2 text-3xl font-black">2027</p>
              <p className="mt-2 text-sm text-purple-100">
                Announcements and seasonal releases.
              </p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/10 p-5">
              <p className="text-sm text-purple-200">English Dubs</p>
              <p className="mt-2 text-3xl font-black">Tracking</p>
              <p className="mt-2 text-sm text-purple-100">
                Confirmed, pending, and changed.
              </p>
            </div>
          </div>
        </div>

        <div className="relative z-10 mx-auto w-full max-w-lg">
          <div className="rounded-[2rem] border border-white/10 bg-white/10 p-4 shadow-2xl shadow-black/40">
            <Image
              src="/maple.png"
              alt="Maple, AnimeReleaseHub assistant"
              width={900}
              height={1200}
              className="h-auto w-full rounded-[1.5rem] object-contain"
              priority
            />
          </div>
        </div>
      </section>
    </main>
  );
}