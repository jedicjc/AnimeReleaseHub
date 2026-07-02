"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";

type Anime = {
  id: number;
  title: string;
};

type News = {
  id: number;
  title: string;
  url: string;
};

type ResultItem =
  | { type: "anime"; id: number; title: string; href: string }
  | { type: "news"; id: number; title: string; href: string };

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ResultItem[]>([]);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  async function search(q: string) {
    if (!q.trim()) {
      setResults([]);
      setOpen(false);
      return;
    }

    const res = await fetch(
      `${API_URL}/search/?query=${encodeURIComponent(q)}`
    );

    const data = await res.json();

    const animeResults: ResultItem[] = (data.anime || []).map((a: Anime) => ({
      type: "anime",
      id: a.id,
      title: a.title,
      href: `/anime/${a.id}`,
    }));

    const newsResults: ResultItem[] = (data.news || []).map((n: News) => ({
      type: "news",
      id: n.id,
      title: n.title,
      href: n.url,
    }));

    const combined = [...animeResults, ...newsResults];

    setResults(combined);
    setActiveIndex(0);
    setOpen(combined.length > 0);
  }

  function handleChange(value: string) {
    setQuery(value);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      search(value);
    }, 250);
  }

  function clearSearch() {
    setQuery("");
    setResults([]);
    setOpen(false);
    setActiveIndex(0);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open || results.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((current) => (current + 1) % results.length);
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((current) =>
        current === 0 ? results.length - 1 : current - 1
      );
    }

    if (e.key === "Escape") {
      setOpen(false);
    }

    if (e.key === "Enter") {
      e.preventDefault();
      window.location.href = results[activeIndex].href;
    }
  }

  useEffect(() => {
    const handleClickOutside = () => setOpen(false);
    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, []);

  return (
    <div className="relative mt-6" onClick={(e) => e.stopPropagation()}>
      <input
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Search anime or news..."
        className="w-full rounded-2xl border border-white/10 bg-black/30 px-5 py-4 text-white placeholder-purple-300 outline-none focus:border-pink-400"
      />

      {open && (
        <div className="absolute z-50 mt-2 w-full rounded-2xl border border-white/10 bg-black/90 p-4 shadow-xl backdrop-blur">
          <p className="mb-2 text-xs font-bold text-purple-300">
            Maple Search Results
          </p>

          <div className="space-y-2">
            {results.map((item, index) => {
              const active = index === activeIndex;

              const className = `block rounded-xl px-3 py-2 text-sm transition ${
                active ? "bg-pink-500/30 text-white" : "bg-white/5 hover:bg-white/10"
              }`;

              if (item.type === "anime") {
                return (
                  <Link
                    key={`${item.type}-${item.id}`}
                    href={item.href}
                    onClick={clearSearch}
                    className={className}
                  >
                    🎬 {item.title}
                  </Link>
                );
              }

              return (
                <a
                  key={`${item.type}-${item.id}`}
                  href={item.href}
                  target="_blank"
                  rel="noreferrer"
                  onClick={clearSearch}
                  className={className}
                >
                  📰 {item.title}
                </a>
              );
            })}
          </div>

          <p className="mt-3 text-xs text-purple-400">
            Use ↑ ↓ to navigate, Enter to open, Esc to close.
          </p>
        </div>
      )}
    </div>
  );
}
