"use client";

import { use, useEffect, useState } from "react";
import { Article, fetchNews } from "@/lib/api";
import NewsCard from "@/components/NewsCard";
import { Loader2 } from "lucide-react";

export default function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  // Unwrap dynamic params (Next.js 15 requirement)
  const resolvedParams = use(params);

  // Capitalize category for display
  const categoryName = resolvedParams.category.charAt(0).toUpperCase() + resolvedParams.category.slice(1);

  useEffect(() => {
    async function fetchCategoryNews() {
      setLoading(true);
      try {
        const data = await fetchNews(categoryName, undefined);
        setArticles(data);
      } catch (error) {
        console.error("Failed to fetch category news", error);
      } finally {
        setLoading(false);
      }
    }
    fetchCategoryNews();
  }, [categoryName]);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">
        Latest in <span className="text-blue-400">{categoryName}</span>
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
          <p className="text-slate-400">There are currently no articles in this category.</p>
        </div>
      )}
    </div>
  );
}
