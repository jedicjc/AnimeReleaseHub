import { DashboardData } from "@/types/dashboard";
import { API_URL } from "@/lib/config";

export type Anime = {
  id: number;
  title: string;
  status: string;
  release_year: number | null;
  release_season: string | null;
  streaming_platform: string | null;
  english_dub_status: string;
  source_url: string | null;
  poster_url: string | null;
  synopsis: string | null;
  score: number | null;
  genres: string | null;
  notes?: string | null;
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
      category_counts: {},
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

export async function getTrending() {
  const response = await fetch(`${API_URL}/trending/`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return [];
  }

  return response.json();
}
