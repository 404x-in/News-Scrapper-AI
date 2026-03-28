"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Article, fetchNews } from "@/lib/api";
import NewsCard from "@/components/NewsCard";
import { Loader2 } from "lucide-react";

function HeadlinesContent() {
  const searchParams = useSearchParams();
  const search = searchParams.get("search");

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHeadlines() {
      setLoading(true);
      try {
        const data = await fetchNews(undefined, search || undefined);
        setArticles(data);
      } catch (error) {
        console.error("Failed to fetch headlines", error);
      } finally {
        setLoading(false);
      }
    }
    fetchHeadlines();
  }, [search]);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">
        {search ? `Search Results: "${search}"` : "Latest Headlines"}
      </h1>

      {loading ? (
        <div className="flex justify-center my-20">
          <Loader2 className="animate-spin text-blue-500 w-12 h-12" />
        </div>
      ) : articles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {articles.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-slate-800 rounded-xl border border-slate-700">
          <h2 className="text-2xl font-bold mb-2">No news found</h2>
          <p className="text-slate-400">Try adjusting your search query.</p>
        </div>
      )}
    </div>
  );
}

export default function HeadlinesPage() {
  return (
    <Suspense fallback={<div className="flex justify-center my-20"><Loader2 className="animate-spin text-blue-500 w-12 h-12" /></div>}>
      <HeadlinesContent />
    </Suspense>
  );
}
