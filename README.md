# 🚀 Documind: Next-Gen Autonomous Financial Intelligence Workstation

[![Status](https://img.shields.io/badge/Status-HYPER--SPRINT%20ACTIVE-brightgreen?style=for-the-badge&logo=rocket)](https://github.com/Thorat-Kaustubh/Documind)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/Frontend-React%20%2F%20Tailwind-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)

> **Documind** is a high-performance, autonomous financial intelligence platform that leverages specialized **Multi-Model Orchestration** (Groq, Gemini, OpenAI) to synthesize deep market insights, analyze massive regulatory filings, and provide real-time monitoring of the financial landscape.

---

### ⚠️ Active Development Note
**This project is actively being improved with new features and optimizations.** 
We are currently in a high-velocity phase, integrating neural indexing and advanced visual intelligence engines to redefine the financial analyst's workflow.

---

## 🌟 Key Features

- **🧠 Multi-Model Brain**: Intelligent task routing across **Groq**, **Gemini**, and **OpenAI** to optimize for latency, context length, and logical reasoning.
- **📈 Visual Intelligence Engine**: Transforms raw LLM data into interactive, production-ready charts using **Recharts** and tailored JSON schemas.
- **🏢 Deep Document Synthesis**: Massive context window support (Gemini 1.5 Pro) for analyzing 200+ page annual reports, historical filings, and complex technical charts.
- **⚡ Autonomous Market Heartbeat**: Background "Observer" agents that monitor Nifty 50, alert on volume shocks, and provide real-time sentiment scoring.
- **🕸️ High-Speed Data Extraction**: Firecrawl-powered scraping that converts complex financial news and regulatory pages into clean, LLM-ready Markdown in milliseconds.
- **💎 Bloomberg Dark UI**: A premium, "glassmorphism" interface built with **Framer Motion** and **Tailwind CSS** for a professional financial experience.

---

## 🏗️ Technical Architecture

Documind operates on a **Hybrid Intelligence Architecture** where specialized models handle specific cognitive tasks, augmented by a high-speed parallel discovery layer.

### 🎭 Multi-Model Tiering

| Tier | Model | Provider | Mission Critical Task | Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Core** | `llama-3.3-70b-versatile` | Groq | **The Architect**: Heavy reasoning, complex synthesis, and structured JSON generation. | < 0.5s |
| **Fast** | `llama-3.1-8b-instant` | Groq | **The Shredder**: High-speed data extraction, DOM cleaning, and sub-300ms fallback layer. | < 0.3s |
| **Grounding** | `gemini-2.5-flash-lite` | Google | **The Pulse Tracker**: Real-time fact-checking and news grounding with Google Search integration. | ~5s |
| **Research** | `gemini-3.1-flash-lite-preview` | Google | **The Investigator**: Deep-dive synthesis of search results for broad intelligence reports. | ~8s |
| **Chat** | `gemini-3.1-flash-lite-preview` | Google | **The Master Bot**: Memory-rich, high-context conversations (Reuses Research Tier). | ~6s |

### 🚀 Hybrid Research Layer
To achieve sub-6s "Live Discovery," Documind bypasses standard model tool-loops:
1.  **Parallel Discovery**: **Tavily API** fetches live financial sources in parallel (sub-1s).
2.  **Context Injection**: Search results are injected directly into the LLM's `raw_context`.
3.  **Single-Pass Synthesis**: The model generates the final report in a single hit, eliminating slow internal "thought" cycles.

---

## 🛠️ Tech Stack

- **🤖 Intelligence Layers**: 
  - **Gemini 3.1 Lite / 2.0 Flash** (Context, Research & Master Chat)
  - **Llama 3.3 / 3.1 via Groq** (Extreme Latency Intent Prediction & Extraction)
- **🧠 Agentic Orchestration**: 
  - **AIBroker (Proprietary)**: Custom task router with semantic caching and cross-provider failover.
  - **Semantic Prompt Compression**: High-fidelity context summarization (Llama-3.1-8B) for massive data handles.
  - **Cross-LLM Resilliency**: Automatic fallback from Gemini to Groq on rate limits or context overflow.
- **🕸️ Research & Extraction**: 
  - **Tavily Search API**: High-speed grounding & advanced discovery engine.
  - **Firecrawl**: JavaScript-heavy scraping for clean financial Markdown.
- **📦 Backend & Infrastructure**: 
  - **FastAPI**: Asynchronous Python core.
  - **Supabase**: PostgreSQL for session state & user data.
  - **ChromaDB**: Vector store for semantic financial memory.
- **🎨 Frontend Experience**: 
  - **React + Tailwind CSS** (Next-gen Bloomberg-Dark interface).
  - **Recharts**: Dynamic financial visualization.
  - **Streamlit**: Integrated forensic diagnostic dashboards.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Thorat-Kaustubh/Documind.git
cd Documind
```

### 2. Configure Environment
Create a `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
FIRECRAWL_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
```

### 3. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 4. Launch the Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Roadmap
- [x] Phase 1: Foundation & Scraping Fleet (Firecrawl Integration)
- [x] Phase 2: Multi-LLM Broker & Brain (Task Routing Logic)
- [x] Phase 3: Visual Intelligence Engine (Strict JSON Chart Schemas)
- [x] Phase 4: Autonomous Market Heartbeat (Sentiment & Notification Fleet)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for the future of financial intelligence.
</p>
