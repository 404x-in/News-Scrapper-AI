export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface Article {
  id: number;
  title: string;
  source: string;
  url: string;
  category: string;
  summary: string;
  image_url: string | null;
  priority_score: number;
  published_at: string;
  created_at: string;
}

export interface DailySummary {
  id: number;
  date: string;
  summary_text: string;
  audio_file_path: string | null;
}

export interface BriefingSection {
  label: string;
  emoji: string;
  articles: Article[];
}

export interface BriefingResponse {
  city: string | null;
  district: string | null;
  state: string | null;
  country: string | null;
  local_summary: string | null;
  audio_url: string | null;
  sections: BriefingSection[];
}

export async function fetchNews(
  category?: string,
  search?: string,
  skip: number = 0,
  limit: number = 20,
): Promise<Article[]> {
  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (search) params.append("search", search);
  params.append("skip", skip.toString());
  params.append("limit", limit.toString());

  const res = await fetch(`${API_BASE_URL}/api/news?${params.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch news");
  return res.json();
}

export async function fetchDailySummary(): Promise<DailySummary | null> {
  const res = await fetch(`${API_BASE_URL}/api/daily-summary`, {
    cache: "no-store",
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch daily summary");
  return res.json();
}

export async function fetchTopNews(limit: number = 4): Promise<Article[]> {
  const res = await fetch(`${API_BASE_URL}/api/top-news?limit=${limit}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch top news");
  return res.json();
}

export async function fetchBriefing(
  city?: string,
  district?: string,
  state?: string,
  country?: string,
  sectionLimit: number = 5,
): Promise<BriefingResponse> {
  const params = new URLSearchParams();
  if (city) params.append("city", city);
  if (district) params.append("district", district);
  if (state) params.append("state", state);
  if (country) params.append("country", country);
  params.append("section_limit", sectionLimit.toString());

  const res = await fetch(`${API_BASE_URL}/api/briefing?${params.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch briefing");
  return res.json();
}
