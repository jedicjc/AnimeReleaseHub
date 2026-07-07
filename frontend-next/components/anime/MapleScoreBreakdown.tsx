type Props = {
  breakdown?: Record<string, number> | null;
};

export function MapleScoreBreakdown({ breakdown }: Props) {
  const items = Object.entries(breakdown ?? {});

  if (!items.length) return null;

  return (
    <div className="mt-8 rounded-3xl border border-pink-300/20 bg-white/5 p-6">
      <h3 className="text-xl font-black">
        🍁 Maple Score Breakdown
      </h3>

      <div className="mt-6 space-y-5">
        {items.map(([label, value]) => (
          <div key={label}>
            <div className="mb-2 flex justify-between text-sm">
              <span className="font-semibold text-purple-100">
                {label}
              </span>

              <span className="font-black text-pink-300">
                {value}/5
              </span>
            </div>

            <div className="h-3 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-400 transition-all duration-700"
                style={{
                  width: `${(value / 5) * 100}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
