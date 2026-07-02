export function Navbar() {
  return (
    <nav className="flex items-center justify-between">
      <div className="text-xl font-black">🍁 AnimeReleaseHub</div>

      <div className="hidden gap-6 text-sm text-purple-200 md:flex">
        <span>Anime</span>
        <span>Dubs</span>
        <span>Calendar</span>
        <span>News</span>
      </div>
    </nav>
  );
}