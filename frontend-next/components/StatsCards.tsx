type Props = {
  newsCount: number;
  animeCount: number;
  dubCount: number;
};

export function StatsCards({ newsCount, animeCount, dubCount }: Props) {
  return (
    <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="rounded-3xl bg-black/20 p-5">
        <p className="text-sm text-purple-200">News Articles</p>
        <p className="mt-2 text-4xl font-black">{newsCount}</p>
      </div>

      <div className="rounded-3xl bg-black/20 p-5">
        <p className="text-sm text-purple-200">Dub Updates</p>
        <p className="mt-2 text-4xl font-black">{dubCount}</p>
      </div>

      <div className="rounded-3xl bg-black/20 p-5">
        <p className="text-sm text-purple-200">Anime Tracked</p>
        <p className="mt-2 text-4xl font-black">{animeCount}</p>
      </div>
    </div>
  );
}