import os
import sys
import pandas as pd
import pypdf
from io import StringIO
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to sys.path to allow importing sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_broker import AIBroker
from database.postgres_sync import PostgresSync
from database.vector_storage import VectorStorage

app = FastAPI(title="Documind API", version="1.0.0")

# Enable CORS for frontend
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

class ChatRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "fast" # 'fast', 'deep', 'visual'

@app.get("/")
async def root():
    return {"status": "Documind API is online", "version": "1.0.0"}

@app.post("/api/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this financial document and provide key insights."),
    mode: str = Form("deep")
):
    """
    Financial File Analysis: Handles PDF and CSV uploads for deep fundamental analysis.
    """
    try:
        content = ""
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            # Read CSV content
            bytes_content = await file.read()
            df = pd.read_csv(StringIO(bytes_content.decode('utf-8')))
            content = df.to_string()
        elif filename.endswith('.pdf'):
            # Read PDF content
            pdf_reader = pypdf.PdfReader(file.file)
            for page in pdf_reader.pages:
                content += page.extract_text()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or CSV.")

        # Execute analysis using the broker with file-specific compression
        response = await broker.execute_task(
            prompt, 
            provider_mode=mode, 
            raw_context=content
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Core Chat Endpoint: Combined RAG + Multi-LLM Routing
    """
    try:
        # 1. Search Vector DB for Context (RAG)
        context_results = vector_db.query(request.prompt, n_results=3)
        context_text = ""
        if context_results and context_results['documents']:
            context_text = "\n".join(context_results['documents'][0])
        
        # 2. Execute Task via Broker
        response = await broker.execute_task(
            request.prompt, 
            provider_mode=request.mode, 
            raw_context=context_text
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/metrics")
async def get_metrics():
    return {"metrics": []}

@app.post("/api/admin/scrape")
async def trigger_scrape():
    return {"message": "Scraping fleet initiated in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
