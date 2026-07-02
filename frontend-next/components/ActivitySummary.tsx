import { NewsCategoryBadge } from "@/components/NewsCategoryBadge";

type Props = {
  categoryCounts: Record<string, number>;
};

export function ActivitySummary({ categoryCounts }: Props) {
  const entries = Object.entries(categoryCounts);

  if (entries.length === 0) return null;

  return (
    <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/10 p-8">
      <p className="text-sm text-pink-200">Maple Intelligence</p>
      <h2 className="text-3xl font-black">Today&apos;s Activity</h2>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {entries.map(([category, count]) => (
          <div key={category} className="rounded-3xl bg-black/20 p-5">
            <NewsCategoryBadge category={category} />
            <p className="mt-4 text-4xl font-black">{count}</p>
          </div>
        ))}
      </div>
    </section>
  );
}