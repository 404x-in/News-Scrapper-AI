export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-800 bg-slate-900 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-center text-center">
        <p className="text-slate-400 text-sm">
          &copy; {currentYear} DailyNews AI. All rights reserved.
        </p>
        <p className="text-slate-500 text-xs mt-2">
          News content aggregated from various public sources for informational purposes.
        </p>
      </div>
    </footer>
  );
}
