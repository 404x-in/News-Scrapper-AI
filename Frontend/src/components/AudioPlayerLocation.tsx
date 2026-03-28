"use client";
import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function AudioPlayerLocation({ 
  audioUrl, 
  summaryText, 
  locationLabel 
}: { 
  audioUrl: string; 
  summaryText: string;
  locationLabel: string;
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (audioUrl) {
      audioRef.current = new Audio(`${API_BASE_URL}${audioUrl}`);
      audioRef.current.onended = () => setIsPlaying(false);
    }
  }, [audioUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="relative rounded-2xl border border-teal-700/50 bg-gradient-to-br from-teal-950/60 to-slate-900 p-6 shadow-lg shadow-teal-900/20 overflow-hidden">
      {/* Glow accent */}
      <div className="pointer-events-none absolute -top-10 -left-10 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />
      <div className="absolute top-0 right-0 p-8 opacity-5">
        <Volume2 size={120} className="text-teal-400" />
      </div>

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
        <button 
          onClick={togglePlay}
          className="bg-teal-600 hover:bg-teal-500 text-white rounded-full p-4 shadow-lg shadow-teal-600/30 transition-all hover:scale-105 active:scale-95 flex-shrink-0"
        >
          {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
        </button>
        
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xl">🤖</span>
            <span className="text-xs font-bold uppercase tracking-widest text-teal-400">
              AI Briefing
            </span>
            <span className="ml-auto px-2 py-0.5 rounded-full text-[10px] font-semibold bg-teal-900/60 text-teal-300 border border-teal-700/50">
              {locationLabel}
            </span>
          </div>
          <p className="text-slate-200 text-sm leading-7 font-light relative z-10">
            {summaryText}
          </p>
        </div>
      </div>
    </div>
  );
}
