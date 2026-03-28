# News Scraper & AI Briefer (DailyNews AI)

An intelligent, full-stack application that aggregates, prioritizes, and summarizes news tailored to your exact location. This project uses a FastAPI backend to scrape and process articles, and a Next.js frontend to deliver hyper-relevant, SLM-prioritized news with AI-generated audio briefings.

## 🚀 Features

- **Hyper-Localized News Feed:** Automatically detects your location (via GPS or IP) to deliver news at the City, District, State, National, and International levels.
- **AI Audio Briefings:** Generates a concise, localized, daily audio brief of the most important news using text-to-speech (TTS), giving you a podcast-like experience.
- **Intelligent Headline Prioritization:** Utilizes a local Small Language Model (SLM) to assign priority scores to headlines, surfacing the most impactful news first.
- **Automated News Scraping:** Continuously fetches the latest articles from multiple RSS feeds and sources (e.g., Google News).
- **Modern UI/UX:** Built with Next.js 15 and TailwindCSS for a responsive and seamless viewing and listening experience.

## 🛠️ Tech Stack

**Frontend:**
- [Next.js](https://nextjs.org/) (React 15)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide React](https://lucide.dev/) (Icons)

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) (Python framework)
- [SQLAlchemy](https://www.sqlalchemy.org/) & SQLite (Database)
- Background schedulers for automated tasks
- AI integrations for caching, generating, and speaking summaries

## ⚙️ Prerequisites

- **Python 3.9+**
- **Node.js 18+** & **npm/yarn/pnpm**

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jxhrna/news-scrapper-and-ai-briefer.git
   cd "news-scrapper-and-ai-briefer"
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   ```

## 🚀 Running the Application

You will need to run both the backend and frontend servers simultaneously.

### 1. Start the Backend API
The backend serves the scraped news, handles the database operations, and generates the summaries/TTS.

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```
*The API will be available at `http://localhost:8000`*

### 2. Start the Frontend
The frontend provides the main user interface for viewing and listening to the news.

```bash
cd frontend
npm run dev
```
*The app will be available at `http://localhost:3000`*

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
