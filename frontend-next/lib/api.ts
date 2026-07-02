import { DashboardData } from "@/types/dashboard";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Anime = {
  id: number;
  title: string;
  status: string;
  release_year: number | null;
  release_season: string | null;
  streaming_platform: string | null;
  english_dub_status: string;
  source_url: string | null;
};

export async function getDashboard(): Promise<DashboardData> {
  const response = await fetch(`${API_URL}/dashboard/`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return {
      news_count: 0,
      anime_count: 0,
      dub_count: 0,
      latest_news: [],
    };
  }

  return response.json();
}

export async function getAnime(): Promise<Anime[]> {
  const response = await fetch(`${API_URL}/anime/`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return [];
  }

  return response.json();
}
export async function getAnimeById(id: string): Promise<Anime | null> {
  const response = await fetch(`${API_URL}/anime/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return null;
  }

  return response.json();
}