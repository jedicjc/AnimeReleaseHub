import Image from "next/image";

export function MaplePanel() {
  return (
    <div className="rounded-[2rem] border border-white/10 bg-white/10 p-4">
      <Image
        src="/maple.png"
        alt="Maple, AnimeReleaseHub assistant"
        width={900}
        height={1200}
        className="h-auto w-full rounded-[1.5rem] object-contain"
        priority
      />
    </div>
  );
}