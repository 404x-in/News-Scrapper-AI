"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/headlines?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "Briefing", href: "/briefing" },
    { label: "Headlines", href: "/headlines" },
    { label: "About", href: "/about" },
  ];

  const categories = [
    "World", "India", "Technology", "Business", "Science", "Politics", "Sports", "Entertainment"
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-lg border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between h-auto py-4 md:py-0 md:h-16">
          
          {/* Logo & Main Nav */}
          <div className="flex items-center gap-8 w-full md:w-auto overflow-x-auto scrollbar-hide">
            <Link href="/" className="flex items-center gap-2 flex-shrink-0 group">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white transition-transform group-hover:scale-105">
                D
              </div>
              <h1 className="text-xl font-bold text-white tracking-tight hidden sm:block group-hover:text-blue-400 transition-colors">
                DailyNews AI
              </h1>
            </Link>

            <nav className="flex items-center gap-6 text-sm font-medium flex-nowrap overflow-x-auto shrink-0 pb-1 md:pb-0 scrollbar-hide">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`transition-colors whitespace-nowrap ${
                    pathname === link.href ? "text-blue-400" : "text-slate-300 hover:text-white"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              
              {/* Category Links Inline for Quick Access */}
              <div className="h-4 w-px bg-slate-700 hidden lg:block mx-2"></div>
              {categories.slice(0, 3).map((cat) => (
                <Link
                  key={cat}
                  href={`/news/${cat.toLowerCase()}`}
                  className={`transition-colors whitespace-nowrap hidden lg:block ${
                    pathname === `/news/${cat.toLowerCase()}` ? "text-blue-400" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {cat}
                </Link>
              ))}
            </nav>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="relative w-full md:w-80 shrink-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search news & press enter..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800 border-slate-700 border text-sm rounded-full pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-slate-400 transition-all focus:bg-slate-800/80 hover:bg-slate-700/50"
            />
          </form>

        </div>
      </div>
    </header>
  );
}
