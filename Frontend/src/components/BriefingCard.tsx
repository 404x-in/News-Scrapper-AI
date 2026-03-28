"use client";

import { Article } from "@/lib/api";
import { ExternalLink, Clock } from "lucide-react";

interface BriefingCardProps {
  article: Article;
  isLocal?: boolean;
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const pub = new Date(dateStr);
  const diffMs = now.getTime() - pub.getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function getFlag(article: Article, isLocal: boolean): string {
  if (isLocal) return "📍";
  if (article.priority_score >= 0.8) return "🔴";
  if (article.priority_score <= 0.3 && article.category === "Entertainment") return "🟢";
  return "";
}

export default function BriefingCard({ article, isLocal = false }: BriefingCardProps) {
  const flag = getFlag(article, isLocal);

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex gap-4 p-4 rounded-xl bg-slate-800/60 border border-slate-700 hover:border-blue-500/60 hover:bg-slate-800 transition-all duration-200"
    >
      {/* Left: colored priority bar */}
      <div
        className={`w-1 rounded-full flex-shrink-0 self-stretch ${
          isLocal
            ? "bg-blue-400"
            : article.priority_score >= 0.8
            ? "bg-red-500"
            : article.priority_score >= 0.5
            ? "bg-amber-400"
            : "bg-slate-600"
        }`}
      />

      <div className="flex-1 min-w-0">
        {/* Title row */}
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-semibold text-white leading-snug group-hover:text-blue-300 transition-colors line-clamp-2">
            {flag && <span className="mr-1">{flag}</span>}
            {article.title}
          </h4>
          <ExternalLink
            size={13}
            className="text-slate-500 group-hover:text-blue-400 flex-shrink-0 mt-0.5 transition-colors"
          />
        </div>

        {/* Summary */}
        {article.summary && (
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed line-clamp-2">
            {article.summary}
          </p>
        )}

        {/* Footer: source + time */}
        <div className="flex items-center gap-2 mt-2">
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-900/50 text-blue-300 border border-blue-800/50">
            {article.source}
          </span>
          <span className="flex items-center gap-1 text-[10px] text-slate-500">
            <Clock size={10} />
            {timeAgo(article.published_at)}
          </span>
        </div>
      </div>
    </a>
  );
}
