type Props = {
  category?: string;
};

export function NewsCategoryBadge({ category = "general" }: Props) {
  const normalized = category.toLowerCase();
  const label = normalized.replaceAll("_", " ").toUpperCase();

  const styles =
    normalized === "new_adaptation"
      ? "bg-blue-400/20 text-blue-200 border-blue-300/30"
      : normalized === "sequel"
        ? "bg-purple-400/20 text-purple-200 border-purple-300/30"
        : normalized === "trailer"
          ? "bg-green-400/20 text-green-200 border-green-300/30"
          : normalized === "cast_update"
            ? "bg-yellow-400/20 text-yellow-200 border-yellow-300/30"
            : normalized === "staff_update"
              ? "bg-orange-400/20 text-orange-200 border-orange-300/30"
              : normalized === "dub_update"
                ? "bg-cyan-400/20 text-cyan-200 border-cyan-300/30"
                : normalized === "delay"
                  ? "bg-red-400/20 text-red-200 border-red-300/30"
                  : "bg-white/10 text-purple-200 border-white/10";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold ${styles}`}>
      {label}
    </span>
  );
}