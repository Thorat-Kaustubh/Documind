# Documind v2 - Agent Instruction Manual

## 🤖 Role
You are the primary AI coding assistant for **Documind v2**, a hybrid Neuro-Symbolic financial intelligence platform. Your goal is to help build a structured, scalable, and production-grade enterprise system, migrating away from the legacy LLM-centric and reactive v1 architecture.

## 🏗️ Architecture Overview
*   **System Type:** Hybrid Neuro-Symbolic system with strong orchestration.
*   **Query Flow:** Query Understanding Layer → Execution Orchestrator → Execution Layer (SQL/RAG/LLM) → Response Synthesizer → Frontend.
*   **Observability:** OpenTelemetry, Prometheus, Grafana (monitor latency, cost, errors).

## 🎨 Frontend Guidelines (Next.js)
*   **Framework:** Next.js (App Router preferred, migrated from Vite).
*   **Language:** Strict TypeScript. Avoid `any`.
*   **State Management:** **Zustand**. Use stores like `authStore`, `chatStore`, `dashboardStore`, `uiStore`. *Do not use React Context API or Redux.*
*   **Data Fetching:** **React Query** (TanStack Query) for server state and caching.
*   **API Client:** Use the centralized API client that handles token injection and automatic retries.
*   **Styling:** Tailwind CSS. Use a consistent design system.
*   **UX:** Implement streaming responses, robust auth guards, and proactive error handling.

## ⚙️ Backend Guidelines (FastAPI)
*   **Framework:** FastAPI.
*   **Database:** Supabase/Postgres (structured data), Vector DB (document embeddings), Knowledge Graph (relationships).
*   **Authentication:** Centralized JWT-based auth flow. Frontend → Supabase → JWT → FastAPI Middleware. Ensure endpoints have token verification.
*   **Execution Layer:** 
    *   **SQL Engine:** Postgres for structured financial queries.
    *   **RAG Engine:** Vector DB for document retrieval.
    *   **LLM Engine:** Groq (low-latency tasks) & Gemini (deep reasoning).
*   **Data Pipeline:** Event-driven architecture (Kafka/queue). Use the dedicated **Data Update Microservice** for DB writes to handle validation, transformation, and controlled writes (batching/retries). Do not write directly to the database from scrapers.

## 🧠 AI & Logic Guidelines
*   **Query Understanding:** Implement Intent Classification (DistilBERT), Intent Verification (confidence threshold + LLM fallback), Financial NER, and Query Planning.
*   **Execution Orchestrator:** Route tasks optimally (SQL vs. RAG vs. LLM) based on cost-awareness and latency.
*   **Hallucination Guards:** Always validate sources and provide confidence scores. Provide explainable AI (sources + confidence) to the user.

## 📝 General Rules
*   When creating new features, always consider the impact on observability, performance (caching, latency), and data consistency.
*   Before modifying the database schema, ensure it aligns with the Data Update Microservice constraints.
*   Keep files modular and focused. Do not mix business logic with routing or UI.
