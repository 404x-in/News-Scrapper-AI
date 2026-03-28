export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto py-12">
      <h1 className="text-4xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">
        About DailyNews AI
      </h1>
      
      <div className="space-y-6 text-slate-300 text-lg leading-relaxed">
        <p>
          <strong>DailyNews AI</strong> is a modern, automated news aggregation platform designed to cut through the noise and deliver high-priority current affairs directly to you.
        </p>

        <p>
          In today's fast-paced world, staying informed can be overwhelming. We source articles from trusted global and national publishers—including the BBC, The Hindu, NDTV, and The Times of India—and automatically categorize them into distinct feeds.
        </p>

        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 my-8">
          <h2 className="text-2xl font-bold text-white mb-4">Core Features</h2>
          <ul className="list-disc pl-5 space-y-3">
            <li><strong>Automated Scraping:</strong> Real-time syncing with major publication RSS feeds via a Python scheduled backend.</li>
            <li><strong>Intelligent Summarization:</strong> Extractive summarization limits long-winded articles to easily digestible context.</li>
            <li><strong>Priority Briefings:</strong> A daily synthetic briefing aggregating only the most crucial World, Business, and Politics news.</li>
            <li><strong>Audio Playback:</strong> A seamless native Google Text-to-Speech (gTTS) integration allowing you to listen to your morning briefing like a podcast.</li>
          </ul>
        </div>

        <p>
          Built with a Python FastAPI backend and a Next.js 14 App Router frontend, DailyNews AI is optimized for speed, reliability, and an exceptional dark-mode reading experience.
        </p>
      </div>
    </div>
  );
}
