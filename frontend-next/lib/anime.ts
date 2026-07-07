type AnimeLike = {
  title?: string | null;
  title_english?: string | null;
};

export function getAnimeDisplayTitle(anime: AnimeLike): string {
  return anime.title_english || anime.title || "Unknown Anime";
}
