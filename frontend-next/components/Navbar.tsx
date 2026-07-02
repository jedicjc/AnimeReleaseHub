import Link from "next/link";

export function Navbar() {
  return (
    <nav className="flex items-center justify-between">
      <Link href="/" className="text-xl font-black">
        🍁 AnimeReleaseHub
      </Link>

      <div className="hidden gap-6 text-sm text-purple-200 md:flex">
        <Link href="/" className="hover:text-pink-200">
          Dashboard
        </Link>

        <Link href="/anime" className="hover:text-pink-200">
          Anime
        </Link>

        <span className="opacity-50">Dubs</span>
        <span className="opacity-50">Calendar</span>
        <span className="opacity-50">News</span>
      </div>
    </nav>
  );
}