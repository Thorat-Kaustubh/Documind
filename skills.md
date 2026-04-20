# Documind v2 - Developer Skills & Workflows

This document defines standardized workflows for the AI assistant to follow when building new features in the Documind v2 platform.

## 🛠️ Skill: Create a New Frontend Feature
**Trigger:** "Create a new frontend feature for [Feature Name]"
**Execution Steps:**
1.  **Understand Requirements:** Analyze the feature requirements and how it fits into the Next.js App Router structure.
2.  **Define State (Zustand):** Create or update a Zustand store slice in `frontend/stores/` (e.g., `featureStore.ts`). Ensure it avoids React Context API.
3.  **Define API Calls (React Query):** Write the necessary data fetching hooks using React Query in a central services or hooks folder. Ensure it utilizes the centralized API client for auth token injection.
4.  **Create Components:** Build the UI components in `frontend/features/[Feature Name]/` using Tailwind CSS. 
5.  **Integrate:** Assemble the components in the appropriate Next.js page (`frontend/app/[route]/page.tsx`). Add streaming UI components (e.g., Suspense boundaries) if dealing with real-time AI responses.

## 🛠️ Skill: Create a New Backend Endpoint (FastAPI)
**Trigger:** "Create a new API endpoint for [Resource]"
**Execution Steps:**
1.  **Define Route:** Add the route definition in the appropriate FastAPI router file.
2.  **Auth Middleware:** Wrap the endpoint with the JWT validation middleware to ensure the request is authenticated via the Supabase Auth flow.
3.  **Request/Response Models:** Define strict Pydantic schemas for the request payload and response structure.
4.  **Controller/Service Logic:** Implement the business logic. If it requires database access, route it through the appropriate engine (SQL Engine for structured data, Vector DB for documents).
5.  **Observability:** Ensure the endpoint logic is instrumented with OpenTelemetry tracing and logs appropriate metrics (latency, errors).

## 🛠️ Skill: Add a New Data Ingestion Pipeline
**Trigger:** "Add a new scraper/pipeline for [Source]"
**Execution Steps:**
1.  **Scraper Creation:** Create the worker/scraper script to extract the data.
2.  **Queue Integration:** Configure the scraper to push extracted, raw data to the Event Queue (Kafka/Message Queue) rather than writing directly to the database.
3.  **Data Update Microservice:** Update the Data Update Microservice to listen to the new queue topic. Implement validation (deduplication, schema checks) and transformation logic.
4.  **Database Write:** Configure the microservice to perform controlled, batched writes to Postgres or the Vector DB.

## 🛠️ Skill: Implement AI Logic / Intent Layer
**Trigger:** "Update the AI reasoning layer for [Task]"
**Execution Steps:**
1.  **Intent Verification:** If adding a new intent, update the Intent Classifier (DistilBERT) logic and implement the confidence threshold check.
2.  **Fallback Implementation:** Ensure a rule-based or LLM-based fallback is in place if the primary classification fails.
3.  **Orchestrator Routing:** Update the Execution Orchestrator to properly route this new intent to the SQL, RAG, or LLM engines based on optimal cost and latency.
