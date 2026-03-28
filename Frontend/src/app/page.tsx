"use client";

import { useEffect, useState } from "react";
import { DailySummary, fetchDailySummary, fetchTopNews, Article } from "@/lib/api";
import AudioPlayer from "@/components/AudioPlayer";
import NewsCard from "@/components/NewsCard";
import Link from "next/link";
import { Loader2, ArrowRight } from "lucide-react";

export default function Home() {
  const [dailyBrief, setDailyBrief] = useState<DailySummary | null>(null);
  const [topHeadlines, setTopHeadlines] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHomeData() {
      setLoading(true);
      try {
        const [summary, topNews] = await Promise.all([
          fetchDailySummary(),
          fetchTopNews(4) // fetch top 4 by AI priority score
        ]);
        setDailyBrief(summary);
        setTopHeadlines(topNews);
      } catch (error) {
        console.error("Failed to fetch home data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchHomeData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-500 w-12 h-12" />
      </div>
    );
  }

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

  return (
    <div className="space-y-12">
      {/* Hero Section: Daily Briefing directly on Home */}
      <section className="bg-gradient-to-br from-blue-900/40 to-slate-800 border border-slate-700 rounded-2xl p-8 shadow-xl">
        <h2 className="text-3xl font-extrabold text-white mb-6">
          {greeting}. Here is your Daily Briefing.
        </h2>
        
        {dailyBrief ? (
          <div>
            <AudioPlayer summary={dailyBrief} />
            <div className="text-sm font-medium text-slate-400 bg-slate-900/50 inline-block px-4 py-2 rounded-lg border border-slate-700 mt-2">
              Generated strictly from High Priority Current Affairs
            </div>
          </div>
        ) : (
          <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700 text-center">
            <p className="text-slate-400">No daily briefing generated yet for today.</p>
          </div>
        )}
      </section>

      {/* Top Headlines Section */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <span className="w-2 h-8 bg-blue-500 rounded-full inline-block"></span>
            Top Headlines Worldwide
          </h3>
          <Link href="/headlines" className="text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
            View All <ArrowRight size={16} />
          </Link>
        </div>

        {topHeadlines.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {topHeadlines.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <p className="text-slate-400">No news available.</p>
        )}
      </section>

      {/* Categories Grid */}
      <section className="py-8 border-t border-slate-800">
        <h3 className="text-xl font-bold mb-6">Explore by Category</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {["World", "India", "Business", "Politics", "Technology", "Science", "Sports", "Entertainment"].map((cat) => (
            <Link 
              key={cat} 
              href={`/news/${cat.toLowerCase()}`}
              className="bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl p-6 text-center transition-all hover:border-blue-500 group"
            >
              <h4 className="font-bold text-lg group-hover:text-blue-400 transition-colors">{cat}</h4>
              <p className="text-xs text-slate-400 mt-2">View today's top stories</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
