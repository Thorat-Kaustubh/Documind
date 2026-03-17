# Documind: Full System Implementation Blueprint

This document serves as the master technical specification for the Documind project. It is designed to be used as a sequence of prompts for system implementation.

---

## Phase 1: The Brain (LLM Orchestration & Schema)
**Objective:** Transform `ai_broker.py` from a skeleton into a high-performance routing engine with unified output schemas.

### 1.1 Multi-Provider Integration
*   **Groq (Llama 3.3 70b)**: Implementation for sub-500ms sentiment analysis and rapid responses.
*   **Gemini 2.5 Pro**: Implementation for deep-context financial report analysis and complex reasoning (Full News Articles/PDFs).
*   **Gemini 2.5 Flash**: Implementation for rapid task completion and generating chart specifications with higher free-tier throughput.

### 1.2 Unified JSON Schema
Every LLM response must follow a strict structure:
```json
{
  "summary": "Brief analysis text",
  "sentiment": { "score": 0.85, "label": "Bullish", "confidence": 0.92 },
  "visuals": {
    "type": "line | bar | pie | none",
    "chart_data": [],
    "insight_cards": []
  },
  "sources": ["Firecrawl Extract A", "Postgres Metric B"]
}
```

---

## Phase 2: The Orchestrator (API & Pipeline)
**Objective:** Build the central FastAPI server that bridges the scrapers, the database, and the frontend.

### 2.1 FastAPI Core (`backend/main.py`)
*   **Middleware**: CORS setup for the React frontend.
*   **Endpoints**:
    *   `POST /api/chat`: Takes user prompt -> Queries Vector DB -> Calls `AIBroker` -> Returns Unified JSON.
    *   `GET /api/market/metrics`: Fetches latest price/volume from Postgres.
    *   `POST /api/admin/scrape`: Triggers the `scraping_hub` fleet on-demand.

### 2.2 Shared Memory Integration
*   Link `VectorStorage` (ChromaDB) to the `/api/chat` endpoint to provide "RAG" (Retrieval Augmented Generation) context to the LLMs.

---

## Phase 3: The Visual Intelligence (Frontend Engine)
**Objective:** Implement the "Dynamic Charting" and "Bloomberg Dark" glassmorphism UI.

### 3.1 `VisualPortal` Component
*   Logic to detect the `visuals` key in the LLM response.
*   Map `chart_data` to **Recharts** components (ResponsiveContainer, AreaChart, Toolkit).
*   Implement "Insight Cards" using **Framer Motion** for hover-triggered pop-ups.

### 3.2 Professional Dashboard Polish
*   **Theme**: Deep blacks (`#050505`), neon accents (`#00f2ff`), and glassmorphism borders (`rgba(255,255,255,0.05)`).
*   **Sidebar**: Persistent market heartbeat indicators (Nifty 50, Sensex) with live-feeling transition effects.

---

## Phase 4: The Autonomous Pulse (Monitoring & Watchdogs)
**Objective:** Transition from a "Request-Response" app to an "Autonomous" agent.

### 4.1 The Observer Instance (`backend/observer.py`)
*   A background process using `APScheduler`.
*   **Loop**: Scrape ET/Mint every 15 mins -> Identify "Shock Events" (Volume spikes > 200%) -> Push alerts to the Frontend via WebSockets or long-polling.

### 4.2 Automated Reporting
*   Trigger `Gemini 3.1 Pro` at EOD (End of Day) to generate a "Documind Daily Briefing" based on all collected data in the Vector DB for that day.

---

## Implementation Sequence
1.  **Run Phase 1**: Power the `AIBroker`.
2.  **Run Phase 2**: Build the API Gateway.
3.  **Run Phase 3**: Connect the Dashboard visuals.
4.  **Run Phase 4**: Activate background autonomy.

---
*Status: READY FOR PHASE 1 IMPLEMENTATION*
