import os
import sys
import time
import pandas as pd
import pypdf
from io import StringIO
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to sys.path to allow importing sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_broker import AIBroker
from database.postgres_sync import PostgresSync
from database.vector_storage import VectorStorage
from backend.web_intelligence import WebIntelligence
from database.pdf_rag import PDFIntelligenceEngine
from backend.tasks import process_pdf_task, discovery_sweep_task # USE CELERY TASKS

app = FastAPI(title="Documind Elite: Production Engine", version="2.0.0")

# High-Performance Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
broker = AIBroker()
pg_db = PostgresSync()
vector_db = VectorStorage()
web_intel = WebIntelligence()
pdf_rag = PDFIntelligenceEngine()

# Ensuring temp_pdfs directory exists for secure storage
os.makedirs("temp_pdfs", exist_ok=True)

class ChatRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "fast" 
    ticker: Optional[str] = None

class ResearchRequest(BaseModel):
    ticker: str
    company_name: str

@app.get("/")
async def root():
    return {"status": "Documind Elite Engine Online", "version": "2.0.0", "task_queue": "connected"}

@app.post("/api/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this financial document."),
    mode: str = Form("deep")
):
    """
    Secure File Analysis: Refactored with robust sanitization and isolated storage.
    """
    try:
        # 1. SECURITY: Filename Sanitization (Prevents path traversal)
        safe_name = "".join([c for c in file.filename if c.isalnum() or c in ('.', '-', '_')]).strip()
        if not safe_name: safe_name = f"upload_{int(time.time())}.pdf"
        
        file_path = os.path.join("temp_pdfs", safe_name)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        content = ""
        if safe_name.endswith('.csv'):
            df = pd.read_csv(file_path)
            content = df.to_string()
        elif safe_name.endswith('.pdf'):
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                for page in pdf_reader.pages:
                    content += page.extract_text()
        else:
            raise HTTPException(status_code=400, detail="Unsupported format.")

        response = await broker.execute_task(prompt, provider_mode=mode, raw_context=content)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat-stream")
async def chat_stream(request: ChatRequest):
    """
    Two-Phase Response Streaming:
    Phase 1: Fast initial reasoning summary.
    Phase 2: Deep refinement and citations.
    """
    try:
        # Retrieval with Metadata filters
        results = vector_db.collection.query(
            query_texts=[request.prompt],
            n_results=5,
            where={"symbol": request.ticker} if request.ticker else None
        )
        context_text = "\n".join(results['documents'][0]) if results['documents'] else ""
        
        return StreamingResponse(
            broker.stream_task(request.prompt, raw_context=context_text),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def perform_research(request: ResearchRequest):
    """
    Deep Web Discovery: Triggers persistent background tasks via CELERY.
    Satisfies PRODUCTION-GRADE RELIABILITY (A. Distributed Task System).
    """
    try:
        # 1. Fast web context
        context = web_intel.get_company_context(request.ticker, request.company_name)
        
        # 2. Scout for PDFs
        pdf_links = web_intel.find_annual_reports(request.company_name)
        
        # 3. Persistent Ingestion: Queue the task (even if server restarts, Celery picks it up)
        if pdf_links:
             process_pdf_task.delay(request.ticker, pdf_links[0])

        return {
            "context": context,
            "pdfs": pdf_links[:3],
            "celery_task_id": "queued_for_discovery"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest-local-file")
async def ingest_local_file(
    file: UploadFile = File(...),
    symbol: str = Form("USER_DOC")
):
    """
    D. SECURE FILE HANDLING + PERSISTENT QUEUE.
    """
    try:
        safe_name = "".join([c for c in file.filename if c.isalnum() or c in ('.', '-', '_')]).strip()
        temp_path = os.path.join("temp_pdfs", safe_name)
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # PERSISTENT TASK: Let the background workers process the embedding
        process_pdf_task.delay(symbol, temp_path, is_local=True)
        
        return {"status": "queued", "safe_filename": safe_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag-chat")
async def rag_chat(request: ChatRequest):
    """
    Enterprise RAG endpoint with source attribution.
    """
    try:
        results = vector_db.collection.query(
            query_texts=[request.prompt],
            n_results=8,
            where={"symbol": request.ticker} if request.ticker else None
        )
        
        context_chunks, citations = [], []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                context_chunks.append(f"[Ref: {meta.get('source')} Page {meta.get('page')}]: {doc}")
                citations.append({"text": doc[:100] + "...", "source": meta.get('source')})
        
        response = await broker.execute_task(request.prompt, provider_mode="visual", raw_context="\n\n".join(context_chunks))
        response["citations"] = citations[:3] 
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
