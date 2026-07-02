import Image from "next/image";

type Props = {
  title?: string | null;
  posterUrl?: string | null;
};

export function AnimePoster({ title, posterUrl }: Props) {
  const safeTitle = title ?? "Unknown Anime";

  const initials = safeTitle
    .split(" ")
    .slice(0, 2)
    .map((w) => w?.[0] ?? "")
    .join("")
    .toUpperCase();

  return (
    <div className="group relative aspect-[3/4] overflow-hidden rounded-3xl border border-white/10 bg-black/30">
      {posterUrl ? (
        <Image
          src={posterUrl}
          alt={safeTitle}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-110"
        />
      ) : (
        <div className="flex h-full items-center justify-center bg-gradient-to-br from-pink-500/20 via-purple-500/10 to-blue-500/20">
          <div className="text-center">
            <p className="text-5xl font-black text-white/90">
              {initials || "?"}
            </p>
            <p className="mt-3 text-sm text-purple-200">
              {safeTitle}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}