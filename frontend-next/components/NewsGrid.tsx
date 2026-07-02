import { NewsArticle } from "@/types/dashboard";
import { NewsCategoryBadge } from "@/components/NewsCategoryBadge";

type Props = {
  articles: NewsArticle[];
};

export function NewsGrid({ articles }: Props) {
  return (
    <section className="mt-8 rounded-[2rem] border border-white/10 bg-white/10 p-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-pink-200">Maple Scout</p>
          <h2 className="text-3xl font-black">Latest News</h2>
        </div>

        <p className="text-sm text-purple-200">
          Showing {articles.length} articles
        </p>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        {articles.map((article) => (
          <a
            key={article.id}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-3xl border border-white/10 bg-black/20 p-5 transition hover:bg-white/10"
          >
            <p className="text-lg font-bold">{article.title}</p>

            <div className="mt-3 flex items-center gap-2">
              <NewsCategoryBadge category={article.category} />

              <span className="text-sm text-purple-200">
                {article.source}
              </span>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}