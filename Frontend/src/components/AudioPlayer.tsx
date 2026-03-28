"use client";
import { useEffect, useRef, useState } from "react";
import { DailySummary } from "@/lib/api";
import { Play, Pause, Volume2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function AudioPlayer({ summary }: { summary: DailySummary }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (summary.audio_file_path) {
      audioRef.current = new Audio(`${API_BASE_URL}${summary.audio_file_path}`);
      audioRef.current.onended = () => setIsPlaying(false);
    }
  }, [summary]);

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
    <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-2xl p-6 shadow-xl text-white mb-8 border border-blue-700/50 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-10">
        <Volume2 size={120} />
      </div>
      
      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
        <button 
          onClick={togglePlay}
          className="bg-blue-500 hover:bg-blue-400 text-white rounded-full p-5 shadow-lg shadow-blue-500/30 transition-all hover:scale-105 active:scale-95 flex-shrink-0"
        >
          {isPlaying ? <Pause size={32} /> : <Play size={32} className="ml-1" />}
        </button>
        
        <div>
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
            Daily News Briefing 
            <span className="text-sm font-normal bg-blue-800/80 px-3 py-1 rounded-full text-blue-200">
              {summary.date}
            </span>
          </h2>
          <p className="text-blue-100 text-sm md:text-base leading-relaxed opacity-90 max-w-4xl">
            {summary.summary_text}
          </p>
        </div>
      </div>
    </div>
  );
}
