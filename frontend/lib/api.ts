export type SearchItem = {
  id: string;
  title: string;
  year: number | null;
  poster: string | null;
  languages: string[];
  qualities: string[];
  score: number;
};

export type SearchResponse = {
  query: string;
  page: number;
  page_size: number;
  total: number;
  items: SearchItem[];
};

export type MediaDetails = {
  id: string;
  title: string;
  description: string;
  year: number | null;
  genre: string[];
  languages: string[];
  qualities: string[];
  versions: string[];
  runtime: number | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchSearch(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load search results");
  }
  return response.json();
}

export async function fetchRecent(): Promise<SearchItem[]> {
  const response = await fetch(`${API_BASE}/recent`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load recent items");
  }
  const payload = (await response.json()) as Array<MediaDetails & { id: string }>;
  return payload.map((item) => ({
    id: item.id,
    title: item.title,
    year: item.year,
    poster: null,
    languages: item.languages,
    qualities: item.qualities,
    score: 100,
  }));
}

export async function fetchMedia(id: string): Promise<MediaDetails> {
  const response = await fetch(`${API_BASE}/movie/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Media not found");
  }
  return response.json();
}
