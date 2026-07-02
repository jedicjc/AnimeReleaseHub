export type NewsArticle = {
  id: number;
  title: string;
  source: string;
  url: string;
  category?: string;
  created_at?: string;
};

export type DashboardData = {
  news_count: number;
  anime_count: number;
  dub_count: number;
  latest_news: NewsArticle[];
  category_counts: Record<string, number>;
};