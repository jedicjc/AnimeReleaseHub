export function MapleInsight({ insight }: { insight: string }) {
  if (!insight) return null;

  return (
    <section className="rounded-3xl border border-pink-300/20 bg-gradient-to-r from-pink-500/10 via-purple-500/10 to-cyan-500/10 p-6">
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-pink-500/20 text-2xl">
          🍁
        </div>

        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-pink-300">
            Today&apos;s Maple Insight
          </p>

          <p className="mt-3 text-lg leading-relaxed text-purple-100">
            {insight}
          </p>
        </div>
      </div>
    </section>
  );
}
