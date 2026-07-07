"use client";

import { AskMaplePanel } from "@/components/anime/AskMaplePanel";

type AskMapleProps = {
  animeId: number;
};

export default function AskMaple({ animeId }: AskMapleProps) {
  return <AskMaplePanel animeId={animeId} />;
}
