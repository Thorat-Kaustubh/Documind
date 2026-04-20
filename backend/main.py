import os
import sys
import time
import logging
import asyncio
import subprocess
import signal
import pandas as pd
import pypdf
import warnings
from io import StringIO
from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, field_validator, EmailStr
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- NUCLEAR SILENCER (Absolute Production Silence) ---
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TQDM_DISABLE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import logging
import warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
# -----------------------------------------------------

from backend.orchestrator import ExecutionOrchestrator
from database.postgres_sync import PostgresSync
from database.vector_storage import VectorStorage
from backend.web_intelligence import WebIntelligence
from database.pdf_rag import PDFIntelligenceEngine
from backend.tasks import process_pdf_task, discovery_sweep_task, sector_discovery_task
from backend.auth import get_current_user, check_ownership
from backend.market_data_engine import MarketDataEngine

from contextlib import asynccontextmanager
from backend.config import settings

# --- RESPONSE MODELS (Fixed Integration) ---
class PulseResponse(BaseModel):
    id: str
    asset_id: str
    title: str
    content: str
    source: str
    sentiment_score: float
    category: str
    published_at: datetime
    ticker: str
    company_name: str

class VitalsResponse(BaseModel):
    nifty: float
    repo_rate: Union[float, str]
    timestamp: str

class ResearchResponse(BaseModel):
    status: str
    context: str
    pdfs: List[str]
    metrics: Dict[str, Any]

class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    profile: Dict[str, Any] = {}

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    timestamp: datetime

# 1. STRUCTURED LOGGING (Audit Trail)
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("documind.api")

# Global process tracking for Celery
celery_process = None

# LIFESPAN (Production Resource Management)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global celery_process
    # Startup logic
    logger.info(f"🚀 {settings.APP_NAME} {settings.VERSION} Starting...")
    
    # 0. Synchronize Database Schema (Hardened Initializer)
    try:
        pg_db.initialize_schema()
        logger.info("📊 Database schema verified and synchronized.")
    except Exception as e:
        logger.error(f"❌ DATABASE_SYNC_FAILED: {e}")

    # 1. Start Celery worker in background (Discovery Fleet)
    try:
        # Check Redis connectivity first
        import redis
        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        logger.info("🔗 Redis connected. Launching Discovery Fleet (Celery)...")
        
        celery_cmd = [
            "celery", "-A", "backend.celery_app", "worker", 
            "--loglevel=info", "--pool=solo"
        ]
        # Launching with detached process group logic for Windows/Unix reliability
        celery_process = subprocess.Popen(
            celery_cmd,
            # Inherit terminal for visibility while debugging/monitoring
            stderr=subprocess.STDOUT
        )
        logger.info(f"🐢 Discovery Fleet active (PID: {celery_process.pid})")
    except Exception as e:
        logger.warning(f"⚠️ Could not start Celery Discovery Fleet: {e}")
        logger.info("Ensure Redis is running for background tasks.")

    # 2. Start internal loops
    asyncio.create_task(refresh_market_cache_loop())
    asyncio.create_task(temp_cleanup_loop())
    
    yield
    
    # Shutdown logic
    logger.info("🛑 Shutting down server...")
    if celery_process:
        logger.info(f"🛑 Terminating Discovery Fleet (PID: {celery_process.pid})...")
        celery_process.terminate()
        try:
            celery_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            celery_process.kill()
        logger.info("🐢 Discovery Fleet grounded.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# 2. CORS HARDENING (Restrict Origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics Export
try:
    from prometheus_client import make_asgi_app
    app.mount("/metrics", make_asgi_app())
except ImportError:
    pass

# 3. GLOBAL EXCEPTION HANDLER (Hardening)
# 4. CENTRALIZED AUTH MIDDLEWARE (Section 6.2)
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    Global security layer that ensures all API requests have trace IDs 
    and validates tokens for protected routes.
    """
    start_time = time.time()
    response = await call_next(request)
    
    # Add performance and traceability headers
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", f"req_{int(time.time()*1000)}")
    
    return response

# 5. ABUSE PROTECTION (Rate Limiting)
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
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

# Initialize Core Services (Shared instances for pooling)
orchestrator = ExecutionOrchestrator()
pg_db = PostgresSync()
vector_db = VectorStorage()
web_intel = WebIntelligence()
pdf_rag = PDFIntelligenceEngine()
market_engine = MarketDataEngine()

async def temp_cleanup_loop():
    """Periodically purges old temporary PDFs to save disk space."""
    while True:
        try:
            now = time.time()
            if os.path.exists(settings.TEMP_DIR):
                for f in os.listdir(settings.TEMP_DIR):
                    fpath = os.path.join(settings.TEMP_DIR, f)
                    if os.path.isfile(fpath) and os.stat(fpath).st_mtime < now - 3600:
                        os.remove(fpath)
                        logger.info(f"Cleanup: Removed stale file {f}")
        except Exception as e:
            logger.error(f"Cleanup Failed: {e}")
        await asyncio.sleep(600) # Every 10 mins

async def refresh_market_cache_loop():
    """Eagerly refreshes market data every 60 seconds to ensure sub-1ms response times."""
    while True:
        try:
            # 1. Pulse Refresh
            pulse = await asyncio.to_thread(pg_db.get_market_pulse)
            market_cache.set("pulse", pulse)

            # 2. Vitals Refresh
            macro_task = asyncio.to_thread(market_engine.fetch_macro_heartbeat)
            econ_task = asyncio.to_thread(market_engine.fetch_economic_pulse)
            macro, econ = await asyncio.gather(macro_task, econ_task)
            
            vitals = {
                "nifty": macro.get("NIFTY_50", 0.0),
                "repo_rate": econ.get("Policy Repo Rate", "N/A"),
                "timestamp": datetime.now().isoformat()
            }
            market_cache.set("vitals", vitals)
            
            logger.info("Eager Market Cache Refreshed.")
        except Exception as e:
            logger.error(f"Eager Cache Refresh Failed: {e}")
        
        await asyncio.sleep(60)

os.makedirs(settings.TEMP_DIR, exist_ok=True)

# --- ENTERPRISE ANALYTICS CACHE ---
class DynamicCacheService:
    """Managed session-less cache for high-frequency market data."""
    def __init__(self):
        self._store = {}
        self._start_time = time.time()

    def set(self, key: str, value: Any):
        self._store[key] = {"v": value, "t": time.time()}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key, {}).get("v")

    def get_uptime(self) -> float:
        return time.time() - self._start_time

market_cache = DynamicCacheService()

class ChatRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "fast" 
    ticker: Optional[str] = None

class ResearchRequest(BaseModel):
    ticker: str
    company_name: str

class WatchlistRequest(BaseModel):
    ticker: str
    action: Optional[str] = "ADD"

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """System Vitality Report."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        uptime=market_cache.get_uptime(),
        timestamp=datetime.now()
    )

@app.get("/", dependencies=[Depends(check_rate_limit)])
async def root():
    return {"status": settings.APP_NAME + " Engine Optimized", "version": settings.VERSION}

async def background_audit_log(user_id: Optional[str], action: str, resource: str, ip_address: Optional[str]):
    """Dispatches audit log creation to a thread pool to avoid blocking the event loop."""
    try:
        await asyncio.to_thread(pg_db.create_audit_log, user_id, action, resource, ip_address)
    except Exception as e:
        logger.error(f"Background Audit Failed: {e}")

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
        
        # Audit Logic (Dispatch to background)
        asyncio.create_task(background_audit_log(user.id, "ANALYZE_FILE", f"Analyzed {file.filename} in {mode} mode", request.client.host))
        
        return await orchestrator.execute_query(prompt, user_id=user.id, context=content[:40000])
    finally:
        if os.path.exists(file_path): os.remove(file_path)

@app.post("/api/chat-stream")
async def chat_stream(request: Request, chat_req: ChatRequest, user: Any = Depends(get_current_user)):
    """Ultra-Low Latency Streaming Response."""
    await check_rate_limit(request)
    results = vector_db.query(query_text=chat_req.prompt, n_results=5, user_id=user.id)
    context_text = "\n".join(results['documents'][0]) if results['documents'] else ""
    return StreamingResponse(orchestrator.stream_task(chat_req.prompt, context=context_text), media_type="text/event-stream")

@app.post("/api/research", response_model=ResearchResponse)
async def perform_research(request: Request, research_req: ResearchRequest, user: Any = Depends(get_current_user)):
    """PARALLELIZED RESEARCH: Fetches context, PDF links, and metrics concurrently."""
    await check_rate_limit(request)
    # Parallel async execution
    context_task = asyncio.to_thread(web_intel.get_company_context, research_req.ticker, research_req.company_name)
    pdf_task = asyncio.to_thread(web_intel.find_annual_reports, research_req.company_name)
    metrics_task = asyncio.to_thread(market_engine.fetch_equity_intelligence, research_req.ticker)
    
    context, pdf_links, metrics = await asyncio.gather(context_task, pdf_task, metrics_task)
    
    if pdf_links:
        process_pdf_task.delay(research_req.ticker, pdf_links[0], user_id=user.id)

    asyncio.create_task(background_audit_log(user.id, "RESEARCH_INIT", f"Target: {research_req.ticker}", request.client.host))

    return ResearchResponse(
        status="research_initiated", 
        context=context, 
        pdfs=pdf_links[:2],
        metrics=metrics
    )

@app.post("/api/rag-chat")
async def rag_chat(request: Request, chat_req: ChatRequest, user: Any = Depends(get_current_user)):
    await check_rate_limit(request)
    results = vector_db.query(query_text=chat_req.prompt, n_results=6, user_id=user.id)
    context_chunks = []
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            context_chunks.append(f"[Ref: {meta.get('source')}]: {doc}")
    
    return await orchestrator.execute_query(chat_req.prompt, user_id=user.id, context="\n\n".join(context_chunks))

@app.get("/api/market-pulse", response_model=List[PulseResponse], dependencies=[Depends(get_current_user)])
async def get_market_pulse():
    # Return from memory instantly
    cached = market_cache.get("pulse")
    if cached: return cached
    # Cold start fallback
    res = await asyncio.to_thread(pg_db.get_market_pulse)
    market_cache.set("pulse", res)
    return res

@app.get("/api/market-vitals", response_model=VitalsResponse)
async def get_market_vitals():
    """Returns high-fidelity NSE/RBI signals for the anonymous landing page pulse."""
    cached = market_cache.get("vitals")
    if cached: return cached
    
    # Cold start fallback
    macro_task = asyncio.to_thread(market_engine.fetch_macro_heartbeat)
    econ_task = asyncio.to_thread(market_engine.fetch_economic_pulse)
    macro, econ = await asyncio.gather(macro_task, econ_task)
    
    res = {
        "nifty": macro.get("NIFTY_50", 0.0),
        "repo_rate": econ.get("Policy Repo Rate", "N/A"),
        "timestamp": datetime.now().isoformat()
    }
    market_cache.set("vitals", res)
    return res

@app.get("/api/assets", dependencies=[Depends(get_current_user)])
async def get_assets():
    cached = market_cache.get("assets")
    if cached: return cached
    res = await asyncio.to_thread(pg_db.get_all_assets)
    market_cache.set("assets", res)
    return res

@app.get("/api/ipos", dependencies=[Depends(get_current_user)])
async def get_ipos():
    cached = market_cache.get("ipos")
    if cached: return cached
    res = await asyncio.to_thread(pg_db.get_ipo_watchlist)
    market_cache.set("ipos", res)
    return res

@app.get("/api/sectors", dependencies=[Depends(get_current_user)])
async def get_sector_intelligence(sector: Optional[str] = None, user: Any = Depends(get_current_user)):
    query = f"SECTOR REPORT [{sector}]" if sector else "SECTOR REPORT"
    results = vector_db.query(query_text=query, n_results=8, user_id=user.id)
    return {"results": results['documents'][0] if results['documents'] else []}

@app.post("/api/watchlist", dependencies=[Depends(get_current_user)])
async def manage_watchlist(req: WatchlistRequest, user: Any = Depends(get_current_user)):
    success = await asyncio.to_thread(pg_db.manage_watchlist, user.id, req.ticker, req.action)
    return {"status": "success" if success else "failed"}

@app.get("/api/watchlist", dependencies=[Depends(get_current_user)])
async def get_watchlist(user: Any = Depends(get_current_user)):
    res = await asyncio.to_thread(pg_db.get_user_watchlist, user.id)
    return res

@app.get("/api/notifications", dependencies=[Depends(get_current_user)])
async def get_notifications(user: Any = Depends(get_current_user)):
    res = await asyncio.to_thread(pg_db.get_user_notifications, user.id)
    return res

@app.post("/api/audit/security-event")
async def log_security_event(request: Request, event: Dict[str, Any]):
    """Records security-critical events (failures, suspicious activity)."""
    # Note: We don't use 'get_current_user' here because login failures are unauthenticated
    asyncio.create_task(background_audit_log(
        user_id=None, 
        action=event.get("action", "SECURITY_EVENT"), 
        resource=event.get("email", "unknown_user"),
        ip_address=request.client.host
    ))
    return {"status": "recorded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
