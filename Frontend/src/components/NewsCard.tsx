"use client";

import Link from "next/link";
import Image from "next/image";
import { Article } from "@/lib/api";
import { useState } from "react";

export default function NewsCard({ article }: { article: Article }) {
  const [imgLoaded, setImgLoaded] = useState(false);
  // Format date to readable string
  const date = new Date(article.published_at).toLocaleString();

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden hover:shadow-lg transition-transform hover:-translate-y-1 border border-slate-700 flex flex-col h-full">
      {article.image_url && (
        <div className="relative w-full h-48 bg-slate-700/30 overflow-hidden">
          {/* Skeleton Placeholder while loading */}
          {!imgLoaded && (
            <div className="absolute inset-0 flex items-center justify-center animate-pulse bg-slate-700 flex-col gap-2 z-0">
               <div className="w-8 h-8 rounded-full bg-slate-600"></div>
               <div className="h-2 bg-slate-600 rounded w-24"></div>
            </div>
          )}
          
          <Image
            src={article.image_url}
            alt={article.title}
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            loading="lazy"
            className={`object-cover transition-opacity duration-500 z-10 relative ${imgLoaded ? "opacity-100" : "opacity-0"}`}
            onLoad={() => setImgLoaded(true)}
            unoptimized // for external RSS images
          />
          <div className="absolute top-2 right-2 bg-blue-600 text-xs text-white px-2 py-1 rounded shadow-lg z-20">
            {article.category}
          </div>
        </div>
      )}
      
      {!article.image_url && (
        <div className="relative w-full h-48 bg-slate-700/30 overflow-hidden">
          <Image
            src="/placeholder.png"
            alt="No Image Available"
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            loading="lazy"
            className="object-cover transition-opacity duration-500 z-10 relative opacity-80"
          />
          <div className="absolute top-2 right-2 bg-blue-600 text-xs text-white px-2 py-1 rounded shadow-lg z-20">
            {article.category}
          </div>
        </div>
      )}

      <div className="p-5 flex flex-col flex-grow">
        <h3 className="text-lg font-bold text-white mb-2 line-clamp-2">
          {article.title}
        </h3>
        <div className="text-sm text-slate-400 mb-3 flex items-center justify-between gap-3">
          <span className="truncate flex-1 font-medium text-slate-300">{article.source}</span>
          <span className="text-xs shrink-0 opacity-70">{date}</span>
        </div>
        <p className="text-slate-300 text-sm mb-4 line-clamp-3 flex-grow">
          {article.summary}
        </p>
        <Link 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex mt-auto text-blue-400 hover:text-blue-300 font-medium text-sm items-center"
        >
          Read Full Article &rarr;
        </Link>
      </div>
    </div>
  );
}
