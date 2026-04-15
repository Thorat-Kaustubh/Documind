import os
import json
import logging
import asyncio
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

from backend.config import settings
from backend.src.shared.schemas import validate_visuals
from backend.src.intelligence import QueryUnderstandingLayer, QueryPlan
from backend.src.execution.llm_engine import LLMEngine
from backend.src.execution.rag_engine import RAGEngine
from backend.src.execution.sql_engine import SQLEngine
from backend.src.shared.cache import TieredCache
from backend.src.intelligence.knowledge_graph import KnowledgeGraphService
from backend.src.shared.performance import PerformanceOptimizer
from backend.src.shared.compression import compressor
from backend.src.shared.observability import ObservabilityManager
from backend.src.intelligence.agent_swarm import AgentSwarm

logger = logging.getLogger("documind.orchestrator")

class ExecutionOrchestrator:
    """
    SECTION 4-12: EXECUTION ORCHESTRATOR (v2.4 - PRODUCTION READY)
    - Full Observability (Section 11).
    - AI Agent Critic & Hallucination Guard (Section 12).
    - Hierarchical Performance & Caching.
    """
    def __init__(self):
        self.intelligence = QueryUnderstandingLayer()
        self.llm_engine = LLMEngine()
        self.rag_engine = RAGEngine()
        self.sql_engine = SQLEngine()
        self.cache = TieredCache()
        self.graph = KnowledgeGraphService()
        self.optimizer = PerformanceOptimizer()
        self.observer = ObservabilityManager()
        self.swarm = AgentSwarm(self.llm_engine)
        
        from tavily import TavilyClient
        self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY) if settings.TAVILY_API_KEY else None

    async def execute_query(self, query: str, user_id: str, context: str = "", user_tier: str = "FREE") -> Dict[str, Any]:
        """
        Main production flow for v2.4.
        """
        # 0. START TRACE (Section 11)
        trace = self.observer.start_trace(query)

        # 1. CACHE CHECK
        cached = self.cache.get_l1(query)
        if cached: return cached

        # 2. UNDERSTAND & PLAN
        start = time.time()
        plan: QueryPlan = await self.intelligence.analyze_query(query)
        self.observer.record_step(trace, "QueryUnderstanding", time.time() - start)
        
        # 3. KNOWLEDGE EXPANSION
        graph_ctx = await self.graph.expand_context(plan.entities.company) if plan.entities.company else ""

        # 4. EXECUTE ENGINES
        start = time.time()
        collected_context = f"{context}\n\n{graph_ctx}"
        execution_tasks = []
        for step in plan.execution_steps:
            if step == "sql": execution_tasks.append(self.sql_engine.fetch_metrics(plan.entities.company or "UNK", plan.entities.metrics or ["revenue"]))
            elif step == "rag": execution_tasks.append(self.rag_engine.retrieve_context(query, user_id, company=plan.entities.company))
            elif step == "web_search": execution_tasks.append(self._fetch_web_data(query))

        if execution_tasks:
            retrieval_results = await asyncio.gather(*execution_tasks)
            for res in retrieval_results: collected_context += f"\n\n{res}"
        self.observer.record_step(trace, "DataIngestion", time.time() - start)

        # 5. PERFORMANCE OPTIMIZATION (Section 10)
        if len(collected_context) > 10000:
            collected_context = await compressor.compress_async(collected_context)
        collected_context = self.optimizer.get_optimal_context(collected_context, user_tier)

        # 6. AGENT CRITIC & SYNTHESIS (Section 12)
        start = time.time()
        # Use simple synthesis for General queries, Agent Critic for deep analysis
        if plan.intent in ["COMPARATIVE_ANALYSIS", "RISK_ASSESSMENT"]:
            response = await self.swarm.analyze_with_critic(query, collected_context)
        else:
            response = await self.llm_engine.generate_response(query, collected_context, mode="fast", system_prompt=self._get_standard_prompt())
        self.observer.record_step(trace, "AISynthesis", time.time() - start)

        # 7. FINAL VALIDATE, CACHE & OBSERVE
        final_response = validate_visuals(response)
        self.observer.complete_trace(trace, final_response, model=self.llm_engine.models["fast"])
        
        if "error" not in final_response:
            self.cache.set_l1(query, final_response)
            
        return final_response

    async def _fetch_web_data(self, query: str) -> str:
        if not self.tavily_client: return "[WEB: Disabled]"
        try:
            search_response = await asyncio.to_thread(self.tavily_client.search, query=query, max_results=3)
            return "\n".join([f"Web: {r['url']}\n{r['content']}" for r in search_response['results']])
        except: return "[WEB: Error]"

    async def stream_task(self, query: str, context: str = ""):
        async for chunk in self.llm_engine.groq_client.chat.completions.create(
            model=self.llm_engine.models["fast"],
            messages=[{"role": "system", "content": "You are Documind."}, {"role": "user", "content": f"CONTEXT: {context[:15000]}\n\nQUERY: {query}"}],
            stream=True
        ):
            if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content

    def _get_standard_prompt(self) -> str:
        return "Act as 'Documind Pulse Engine'. Return valid JSON only. Include summary, sentiment, visuals, and sources."
