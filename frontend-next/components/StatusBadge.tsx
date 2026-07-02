type Props = {
  status: string;
};

export function StatusBadge({ status }: Props) {
  const normalized = status.toLowerCase();

  const label = normalized.replaceAll("_", " ").toUpperCase();

  const styles =
    normalized === "airing"
      ? "bg-green-400/20 text-green-200 border-green-300/30"
      : normalized === "finished"
        ? "bg-red-400/20 text-red-200 border-red-300/30"
        : normalized === "delayed"
          ? "bg-yellow-400/20 text-yellow-200 border-yellow-300/30"
          : "bg-blue-400/20 text-blue-200 border-blue-300/30";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-bold ${styles}`}>
      {label}
    </span>
  );
}