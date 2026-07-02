"use client";

import { useEffect, useState } from "react";

type SearchResult = {
  id: number;
  title: string;
  source: string;
  url: string;
};

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length < 2) {
        setResults([]);
        setSearched(false);
        return;
      }

      setLoading(true);

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/search/?query=${encodeURIComponent(query)}`
        );

        const data = await response.json();
        setResults(data);
        setSearched(true);
      } catch {
        setResults([]);
        setSearched(true);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="mt-8">
      <input
        type="text"
        placeholder="🔍 Search anime news..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full rounded-2xl border border-white/10 bg-black/20 px-5 py-4 text-white placeholder-purple-300 outline-none focus:border-pink-400"
      />

      {loading && (
        <p className="mt-3 text-sm text-purple-200">Maple is searching...</p>
      )}

      {!loading && searched && results.length === 0 && (
        <p className="mt-3 text-sm text-purple-200">No results found.</p>
      )}

      {results.length > 0 && (
        <div className="mt-4 rounded-2xl border border-white/10 bg-black/30 p-4">
          {results.map((article) => (
            <a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-lg p-3 transition hover:bg-white/10"
            >
              <div className="font-semibold">{article.title}</div>
              <div className="text-sm text-purple-300">{article.source}</div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}