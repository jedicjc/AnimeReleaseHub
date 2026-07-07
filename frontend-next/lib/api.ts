import { API_URL } from "@/lib/config";

export type Anime = {
  id: number;
  title: string;
  title_english?: string | null;
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
  japanese_title?: string | null;
  anime_type?: string | null;
  episodes?: number | null;
  rating?: string | null;
  studio?: string | null;
  trailer_url?: string | null;
  members?: number | null;
  favorites?: number | null;
  popularity?: number | null;
  rank?: number | null;
  aired_from?: string | null;
  aired_to?: string | null;
  trend_score?: number | null;
  maple_score?: number | null;
  notes?: string | null;
};

export type AnimeNews = {
  id: number;
  title: string;
  source: string;
  url: string;
  category: string;
  created_at?: string | null;
};

export type AnimeInsight = {
  anime_id: number;
  title: string;
  summary: string;
  score_explanation: string[];
  score_breakdown: Record<string, number>;
};

export type AskMapleResponse = {
  answer: string;
};

export type AskMapleMessage = {
  role: string;
  content: string;
};

export type DashboardPayload = {
  trending: Anime[];
  highest_rated: Anime[];
  latest_news: AnimeNews[];
  upcoming: Anime[];
  maple_picks: Anime[];
  insight: string;
  stats: {
    anime: number;
    news: number;
    trending: number;
    maple_picks: number;
  };
};

function emptyDashboard(): DashboardPayload {
  return {
    trending: [],
    highest_rated: [],
    latest_news: [],
    upcoming: [],
    maple_picks: [],
    insight: "",
    stats: {
      anime: 0,
      news: 0,
      trending: 0,
      maple_picks: 0,
    },
  };
}

export async function getDashboard(): Promise<DashboardPayload> {
  const response = await fetch(`${API_URL}/dashboard/`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return emptyDashboard();
  }

  const dashboard = await response.json();

  if (
    Array.isArray(dashboard.trending) &&
    Array.isArray(dashboard.highest_rated) &&
    Array.isArray(dashboard.latest_news) &&
    Array.isArray(dashboard.upcoming) &&
    Array.isArray(dashboard.maple_picks)
  ) {
    return {
      ...dashboard,
      insight: dashboard.insight ?? "",
      stats: dashboard.stats ?? {
        anime: new Set(
          [
            ...dashboard.trending,
            ...dashboard.highest_rated,
            ...dashboard.upcoming,
            ...dashboard.maple_picks,
          ].map((anime: Anime) => anime.id),
        ).size,
        news: dashboard.latest_news.length,
        trending: dashboard.trending.length,
        maple_picks: dashboard.maple_picks.length,
      },
    };
  }

  const [animeResponse, newsResponse] = await Promise.all([
    fetch(`${API_URL}/anime/`, { cache: "no-store" }),
    fetch(`${API_URL}/news/`, { cache: "no-store" }),
  ]);

  const anime: Anime[] = animeResponse.ok ? await animeResponse.json() : [];
  const latestNews: AnimeNews[] = newsResponse.ok
    ? await newsResponse.json()
    : dashboard.latest_news ?? [];

  const trending = [...anime]
    .sort((a, b) => (b.trend_score ?? 0) - (a.trend_score ?? 0))
    .slice(0, 10);
  const highestRated = [...anime]
    .filter((item) => item.score !== null && item.score !== undefined)
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
    .slice(0, 10);
  const upcoming = anime
    .filter((item) => item.status === "upcoming")
    .slice(0, 10);
  const maplePicks = [...anime]
    .filter((item) => item.score !== null && item.score !== undefined)
    .sort((a, b) => {
      const mapleScore = (item: Anime) => {
        const trend = item.trend_score ?? 0;
        const score = item.score ?? 0;
        const popularity = item.popularity ?? 999999;
        const popularityBonus = Math.max(0, 10000 - popularity) / 1000;
        const upcomingBonus = item.status === "upcoming" ? 10 : 0;

        return trend * 0.5 + score * 5 + popularityBonus + upcomingBonus;
      };

      return mapleScore(b) - mapleScore(a);
    })
    .slice(0, 3);

  return {
    trending,
    highest_rated: highestRated,
    upcoming,
    latest_news: latestNews.slice(0, 10),
    maple_picks: maplePicks,
    insight: "",
    stats: {
      anime: anime.length,
      news: latestNews.length,
      trending: trending.length,
      maple_picks: maplePicks.length,
    },
  };
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

export async function getAnimeNews(
  id: string,
  sourceUrl?: string | null,
): Promise<AnimeNews[]> {
  const response = await fetch(`${API_URL}/anime/${id}/news`, {
    cache: "no-store",
  });

  if (response.ok) {
    const articles: AnimeNews[] = await response.json();

    if (articles.length > 0 || !sourceUrl) {
      return articles;
    }
  }

  if (!sourceUrl) return [];

  const newsResponse = await fetch(`${API_URL}/news/`, {
    cache: "no-store",
  });

  if (!newsResponse.ok) return [];

  const articles: AnimeNews[] = await newsResponse.json();
  return articles.filter((article) => article.url === sourceUrl);
}

export async function getAnimeInsight(
  id: string,
): Promise<AnimeInsight | null> {
  const response = await fetch(`${API_URL}/anime/${id}/insight`, {
    cache: "no-store",
  });

  if (!response.ok) return null;

  return response.json();
}

export async function askMaple(
  id: string,
  question: string,
  history: AskMapleMessage[],
): Promise<AskMapleResponse | null> {
  const response = await fetch(`${API_URL}/anime/${id}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok) return null;

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
