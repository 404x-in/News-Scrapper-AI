"use client";

import { useEffect, useState } from "react";
import {
  BriefingResponse,
  BriefingSection,
  fetchBriefing,
} from "@/lib/api";
import BriefingCard from "@/components/BriefingCard";
import AudioPlayerLocation from "@/components/AudioPlayerLocation";
import { Loader2, MapPin, AlertCircle, RefreshCw } from "lucide-react";

export interface LocationCtx {
  city?: string;
  district?: string;
  state?: string;
  country?: string;
}

type LocationStatus = "idle" | "requesting" | "geocoding" | "done" | "denied" | "error";

async function reverseGeocode(lat: number, lon: number): Promise<LocationCtx> {
  const res = await fetch(`/api/geocode?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error("Geocoding proxy failed");
  const data = await res.json();
  const addr = data.address || {};
  return {
    city: addr.city || addr.town || addr.village || addr.municipality,
    district: addr.county || addr.state_district || addr.district,
    state: addr.state,
    country: addr.country,
  };
}

async function ipFallbackLocation(): Promise<LocationCtx> {
  const res = await fetch("/api/ip-geo");
  if (!res.ok) throw new Error("IP Geocoding proxy failed");
  const data = await res.json();
  return {
    city: data.city,
    state: data.state,
    country: data.country,
  };
}

function SectionBlock({ section, city, state }: { section: BriefingSection; city?: string; state?: string }) {
  const isLocalSection =
    (city && section.label.includes("City")) || 
    (state && section.label.includes("State")) ||
    section.label.includes("District");

  return (
    <div className="space-y-3">
      {/* Section header */}
      <div className="flex items-center gap-2.5 pb-2 border-b border-slate-700/60">
        <span className="text-2xl">{section.emoji}</span>
        <h2 className="text-lg font-bold text-white">{section.label}</h2>
        <span className="ml-auto text-xs text-slate-500 font-medium">
          {section.articles.length} stories
        </span>
      </div>

      <div className="grid gap-2.5">
        {section.articles.map((article) => (
          <BriefingCard
            key={article.id}
            article={article}
            isLocal={isLocalSection}
          />
        ))}
      </div>
    </div>
  );
}

export default function BriefingPage() {
  const [locationStatus, setLocationStatus] = useState<LocationStatus>("idle");
  const [geoErrorMsg, setGeoErrorMsg] = useState<string | null>(null);
  const [location, setLocation] = useState<LocationCtx | null>(null);
  const [briefing, setBriefing] = useState<BriefingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Manual location overrides
  const [showManualInput, setShowManualInput] = useState(false);
  const [manualCity, setManualCity] = useState("");
  const [manualState, setManualState] = useState("");

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const timeStr = now.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });

  async function loadBriefing(loc: LocationCtx) {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBriefing(
        loc.city,
        loc.district,
        loc.state,
        loc.country
      );
      setBriefing(data);
    } catch (e) {
      setError("Failed to load briefing. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function requestLocation() {
    setLocationStatus("requesting");
    setGeoErrorMsg(null);
    if (!navigator.geolocation) {
      setLocationStatus("error");
      // fallback: load without location
      const loc: LocationCtx = {};
      setLocation(loc);
      loadBriefing(loc);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        setLocationStatus("geocoding");
        try {
          const loc = await reverseGeocode(pos.coords.latitude, pos.coords.longitude);
          setLocation(loc);
          setLocationStatus("done");
          loadBriefing(loc);
        } catch (err: any) {
          tryIpFallback();
        }
      },
      async (geoErr) => {
        tryIpFallback();
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: Infinity }
    );

    async function tryIpFallback() {
      setLocationStatus("geocoding");
      try {
        const loc = await ipFallbackLocation();
        setLocation(loc);
        setLocationStatus("done");
        setGeoErrorMsg("GPS blocked - inferred location from IP");
        loadBriefing(loc);
      } catch (err) {
        setLocationStatus("denied");
        setGeoErrorMsg("Position unavailable & IP fallback failed.");
        const loc: LocationCtx = {};
        setLocation(loc);
        loadBriefing(loc);
      }
    }
  }

  useEffect(() => {
    requestLocation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const loc: LocationCtx = {
      city: manualCity.trim() || undefined,
      state: manualState.trim() || undefined,
    };
    setLocation(loc);
    setLocationStatus("done");
    setShowManualInput(false);
    loadBriefing(loc);
  };

  const locationLabel =
    locationStatus === "done" && location
      ? [location.city, location.state].filter(Boolean).join(", ")
      : null;

  return (
    <div className="space-y-8 pb-16">
      {/* ─── Header ─── */}
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-blue-950 via-slate-900 to-slate-900 border border-slate-700 p-7 shadow-xl">
        {/* subtle grid pattern */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-5"
          style={{
            backgroundImage:
              "repeating-linear-gradient(0deg,transparent,transparent 39px,#94a3b8 39px,#94a3b8 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,#94a3b8 39px,#94a3b8 40px)",
          }}
        />

        <div className="relative">
          <h1 className="text-3xl font-extrabold text-white leading-tight mt-2">
            {locationLabel ? (
              <>
                {locationLabel}
                <span className="text-blue-400"> · </span>
                {dateStr}
              </>
            ) : (
              "Your Personalized News Briefing"
            )}
          </h1>

          <p className="text-slate-400 text-sm mt-1">{timeStr} IST</p>

          {/* Location status indicator */}
          <div className="mt-4 flex items-center gap-2">
            {locationStatus === "done" && location?.city && (
              <span className="inline-flex items-center gap-1.5 text-xs bg-blue-900/50 text-blue-300 border border-blue-800/50 px-3 py-1 rounded-full">
                <MapPin size={11} />
                {[location.city, location.district, location.state].filter(Boolean).join(" · ")}
              </span>
            )}
            {(locationStatus === "denied" || locationStatus === "error" || (locationStatus === "done" && geoErrorMsg && geoErrorMsg.includes("IP"))) && (
              <span className={`inline-flex items-center gap-1.5 text-xs border px-3 py-1 rounded-full ${
                locationStatus === "done" ? "bg-amber-900/40 text-amber-400 border-amber-800/50" : "bg-red-500/10 text-red-400 border-red-500/20"
              }`}>
                <AlertCircle size={11} />
                {geoErrorMsg || "Location access failed"}
              </span>
            )}
             {(locationStatus === "requesting" || locationStatus === "geocoding") && (
              <span className="inline-flex items-center gap-1.5 text-xs bg-slate-800 text-slate-400 border border-slate-700 px-3 py-1 rounded-full">
                <Loader2 size={11} className="animate-spin" />
                {locationStatus === "geocoding" ? "Resolving location…" : "Requesting location…"}
              </span>
            )}
            {(locationStatus === "done" || locationStatus === "denied" || locationStatus === "error") && !showManualInput && (
              <div className="flex gap-2">
                <button
                  onClick={() => { setLocationStatus("idle"); requestLocation(); }}
                  className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2 py-1 rounded-full hover:bg-slate-800 transition-colors"
                >
                  <RefreshCw size={11} />
                  Auto Geo
                </button>
                <button
                  onClick={() => setShowManualInput(true)}
                  className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2 py-1 rounded-full hover:bg-slate-800 transition-colors"
                >
                  <MapPin size={11} />
                  Set Manually
                </button>
              </div>
            )}
          </div>
          
          {showManualInput && (
            <form onSubmit={handleManualSubmit} className="mt-4 flex flex-wrap gap-2 items-center bg-slate-800/50 p-2 rounded-lg border border-slate-700/50 block">
              <input
                type="text"
                placeholder="City (e.g. Mumbai)"
                value={manualCity}
                onChange={(e) => setManualCity(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500 w-40"
              />
              <input
                type="text"
                placeholder="State (e.g. Maharashtra)"
                value={manualState}
                onChange={(e) => setManualState(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500 w-48"
              />
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                Go
              </button>
              <button
                type="button"
                onClick={() => setShowManualInput(false)}
                className="text-slate-400 hover:text-white px-2 py-1.5 text-sm"
              >
                Cancel
              </button>
            </form>
          )}
        </div>
      </div>

      {/* ─── Content ─── */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <Loader2 className="animate-spin text-blue-500 w-10 h-10" />
          <p className="text-slate-400 text-sm">Assembling your briefing…</p>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3 text-center">
          <AlertCircle className="text-red-400 w-10 h-10" />
          <p className="text-slate-300 font-medium">{error}</p>
          <button
            onClick={() => location && loadBriefing(location)}
            className="mt-2 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : briefing && briefing.sections.length > 0 ? (
        <div className="space-y-8">
          {/* ─── AI Location Brief ─── */}
          {briefing.local_summary && (
            briefing.audio_url ? (
              <AudioPlayerLocation 
                audioUrl={briefing.audio_url} 
                summaryText={briefing.local_summary} 
                locationLabel={[briefing.city, briefing.state].filter(Boolean).join(", ") || "Your Region"} 
              />
            ) : (
              <div className="relative rounded-2xl border border-teal-700/50 bg-gradient-to-br from-teal-950/60 to-slate-900 p-6 shadow-lg shadow-teal-900/20 overflow-hidden">
                {/* Glow accent */}
                <div className="pointer-events-none absolute -top-10 -left-10 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />

                <div className="relative">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">🤖</span>
                    <span className="text-xs font-bold uppercase tracking-widest text-teal-400">
                      AI Briefing
                    </span>
                    <span className="ml-auto px-2 py-0.5 rounded-full text-[10px] font-semibold bg-teal-900/60 text-teal-300 border border-teal-700/50">
                      {[briefing.city, briefing.state].filter(Boolean).join(", ") || "Your Region"}
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm leading-7 font-light">
                    {briefing.local_summary}
                  </p>
                </div>
              </div>
            )
          )}

          {/* ─── News sections grid ─── */}
          <div className="grid gap-8 lg:grid-cols-2">
            {briefing.sections.map((section) => (
              <div
                key={section.label}
                className={
                  section.label === "National" || section.label === "International"
                    ? "lg:col-span-2"
                    : ""
                }
              >
                <SectionBlock section={section} city={location?.city} state={location?.state} />
              </div>
            ))}
          </div>
        </div>
      ) : briefing && briefing.sections.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3 text-center">
          <span className="text-5xl">📰</span>
          <p className="text-slate-300 font-medium">No articles in the database yet.</p>
          <p className="text-slate-500 text-sm">
            The scraper runs every 30 minutes. Check back shortly or restart the backend to trigger
            an immediate fetch.
          </p>
        </div>
      ) : null}

      {/* ─── Footer hint ─── */}
      {!loading && !error && briefing && briefing.sections.length > 0 && (
        <p className="text-center text-xs text-slate-600 pt-4">
          💬 Articles are ranked by geographic proximity then AI priority score · Updated every 30 min
        </p>
      )}
    </div>
  );
}
