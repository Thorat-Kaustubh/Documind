import os
import sys
import time
import logging
import asyncio
import pandas as pd
import pypdf
from io import StringIO
from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, field_validator, EmailStr
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_broker import AIBroker
from database.postgres_sync import PostgresSync
from database.vector_storage import VectorStorage
from backend.web_intelligence import WebIntelligence
from database.pdf_rag import PDFIntelligenceEngine
from backend.tasks import process_pdf_task, discovery_sweep_task, sector_discovery_task
from backend.auth import get_current_user, check_ownership

# 1. STRUCTURED LOGGING (Audit Trail)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("documind-performance")

app = FastAPI(
    title="Documind Elite: Optimized Production Engine",
    version="2.2.0",
    docs_url=None, 
    redoc_url=None
)

# 2. CORS HARDENING (Restrict Origins)
allowed_origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 3. ABUSE PROTECTION (Rate Limiting)
class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.hits = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self.hits[key] = [h for h in self.hits[key] if h > now - self.window]
        if len(self.hits[key]) >= self.limit:
            return False
        self.hits[key].append(now)
        return True

api_limiter = RateLimiter(limit=100, window=60) # Increased for performance
ai_limiter = RateLimiter(limit=20, window=60)

async def check_rate_limit(request: Request):
    client_ip = request.client.host
    if not api_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests.")

# Initialize Core Services (Shared instances for pooling)
broker = AIBroker()
pg_db = PostgresSync()
vector_db = VectorStorage()
web_intel = WebIntelligence()
pdf_rag = PDFIntelligenceEngine()

os.makedirs("temp_pdfs", exist_ok=True)

# L1 MEMORY CACHE (Hot Data)
_static_cache = {}

class ChatRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "fast" 
    ticker: Optional[str] = None

class ResearchRequest(BaseModel):
    ticker: str
    company_name: str

@app.get("/", dependencies=[Depends(check_rate_limit)])
async def root():
    return {"status": "Documind Elite Engine Optimized", "version": "2.2.0"}

@app.post("/api/analyze-file")
async def analyze_file(
    request: Request,
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this financial document."),
    mode: str = Form("deep"),
    user: Any = Depends(get_current_user)
):
    await check_rate_limit(request)
    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"u{user.id}_{int(time.time())}{ext}"
    file_path = os.path.join("temp_pdfs", safe_name)

    try:
        # Optimized async write
        content_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # Extraction (Non-blocking)
        content = ""
        if ext == '.pdf':
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                content = "\n".join([p.extract_text() for p in pdf_reader.pages])
        
        return await broker.execute_task(prompt, provider_mode=mode, raw_context=content[:40000])
    finally:
        if os.path.exists(file_path): os.remove(file_path)

@app.post("/api/chat-stream")
async def chat_stream(request: Request, chat_req: ChatRequest, user: Any = Depends(get_current_user)):
    """Ultra-Low Latency Streaming Response."""
    await check_rate_limit(request)
    results = vector_db.query(query_text=chat_req.prompt, n_results=5, user_id=user.id)
    context_text = "\n".join(results['documents'][0]) if results['documents'] else ""
    return StreamingResponse(broker.stream_task(chat_req.prompt, raw_context=context_text), media_type="text/event-stream")

@app.post("/api/research")
async def perform_research(request: Request, research_req: ResearchRequest, user: Any = Depends(get_current_user)):
    """PARALLELIZED RESEARCH: Fetches context and PDF links concurrently."""
    await check_rate_limit(request)
    # Parallel async execution
    context_task = asyncio.to_thread(web_intel.get_company_context, research_req.ticker, research_req.company_name)
    pdf_task = asyncio.to_thread(web_intel.find_annual_reports, research_req.company_name)
    context, pdf_links = await asyncio.gather(context_task, pdf_task)
    
    if pdf_links:
        process_pdf_task.delay(research_req.ticker, pdf_links[0], user_id=user.id)

    return {"status": "research_initiated", "context": context, "pdfs": pdf_links[:2]}

@app.post("/api/rag-chat")
async def rag_chat(request: Request, chat_req: ChatRequest, user: Any = Depends(get_current_user)):
    await check_rate_limit(request)
    results = vector_db.query(query_text=chat_req.prompt, n_results=6, user_id=user.id)
    context_chunks = []
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            context_chunks.append(f"[Ref: {meta.get('source')}]: {doc}")
    
    return await broker.execute_task(chat_req.prompt, provider_mode="core", raw_context="\n\n".join(context_chunks))

@app.get("/api/market-pulse", dependencies=[Depends(get_current_user)])
async def get_market_pulse():
    now = time.time()
    if "pulse" in _static_cache and now - _static_cache["pulse"]["t"] < 30:
        return _static_cache["pulse"]["v"]
    res = await asyncio.to_thread(pg_db.get_market_pulse)
    _static_cache["pulse"] = {"v": res, "t": now}
    return res

@app.get("/api/assets", dependencies=[Depends(get_current_user)])
async def get_assets():
    now = time.time()
    if "assets" in _static_cache and now - _static_cache["assets"]["t"] < 1800:
        return _static_cache["assets"]["v"]
    res = await asyncio.to_thread(pg_db.get_all_assets)
    _static_cache["assets"] = {"v": res, "t": now}
    return res

@app.get("/api/ipos", dependencies=[Depends(get_current_user)])
async def get_ipos():
    now = time.time()
    if "ipos" in _static_cache and now - _static_cache["ipos"]["t"] < 3600:
        return _static_cache["ipos"]["v"]
    res = await asyncio.to_thread(pg_db.get_ipo_watchlist)
    _static_cache["ipos"] = {"v": res, "t": now}
    return res

@app.get("/api/sectors", dependencies=[Depends(get_current_user)])
async def get_sector_intelligence(sector: Optional[str] = None, user: Any = Depends(get_current_user)):
    query = f"SECTOR REPORT [{sector}]" if sector else "SECTOR REPORT"
    results = vector_db.query(query_text=query, n_results=8, user_id=user.id)
    return {"results": results['documents'][0] if results['documents'] else []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
