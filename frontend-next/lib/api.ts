import { DashboardData } from "@/types/dashboard";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

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