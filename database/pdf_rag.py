import os
import hashlib
import json
import httpx
import time
import asyncio
from typing import Dict, Any, List, Optional
from backend.ai_broker import AIBroker
from database.vector_storage import VectorStorage

class PDFIntelligenceEngine:
    """
    HIGH-FIDELITY FINANCIAL DOCUMENT INTELLIGENCE SYSTEM (Securely Multi-tenant)
    Transforms dense PDFs into signal-rich, structure-aware intelligence.
    """
    def __init__(self):
        self.vector_db = VectorStorage(collection_name="pdf_intelligence")
        self.broker = AIBroker()
        self.temp_dir = "temp_pdfs"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load the Fidelity Rules
        prompt_path = os.path.join(os.path.dirname(__file__), "pdf_system_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except:
             self.system_prompt = "Extract financial tables and metrics from the provided PDF content."

    def _get_document_hash(self, file_path: str) -> str:
        """Data Integrity - Compute SHA256 of the PDF."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def process_financial_pdf(self, symbol: str, pdf_url: str, is_local: bool = False, user_id: str = None) -> bool:
        """Fix 4: Hybrid RAG Implementation."""
        try:
            # Step 1: Ingest and Chunk
            res = await self.ingest_document(symbol, pdf_url, user_id=user_id)
            if res["status"] != "SUCCESS": return False
            
            print(f"[Hybrid-RAG] Document for {symbol} vectorized and stored.")
            return True
        except Exception as e:
            print(f"[PDF-ENGINE-CRITICAL-FAILURE]: {e}")
            return False

    def _chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """Split text into overlapping semantic chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    async def ingest_document(self, symbol: str, pdf_url: str, user_id: str = None) -> Dict[str, Any]:
        """Download, PDF-to-Text, Chunk, and Embed."""
        import pypdf
        local_filename = os.path.join(self.temp_dir, f"{symbol}_{int(time.time())}.pdf")
        
        try:
            from scraping_hub.pdf_downloader import PDFDownloadOrchestrator
            downloader = PDFDownloadOrchestrator()
            res = await downloader.execute_retrieval(pdf_url, symbol)
            
            if res["status"] != "SUCCESS":
                return self._trigger_fallback("DOWNLOAD_FAILED", res.get("final_reason"))

            with open(local_filename, "wb") as f:
                f.write(res["data"])

            # PDF Extraction
            content = ""
            with open(local_filename, "rb") as f:
                reader = pypdf.PdfReader(f)
                content = "\n".join([p.extract_text() for p in reader.pages])

            doc_hash = self._get_document_hash(local_filename)
            chunks = self._chunk_text(content)
            
            # Hybrid RAG: Store Chunks
            for i, chunk in enumerate(chunks):
                self.vector_db.upsert_secure(
                    text=chunk,
                    metadata={
                        "symbol": symbol,
                        "source": pdf_url,
                        "chunk_id": i,
                        "doc_hash": doc_hash,
                        "timestamp": time.time(),
                        "user_id": user_id
                    },
                    namespace=f"chunk_{symbol}_{doc_hash[:8]}",
                    user_id=user_id
                )

            return {"status": "SUCCESS", "document_hash": doc_hash}

        except Exception as e:
            return self._trigger_fallback("SYSTEM_ERROR", str(e))
        finally:
            if os.path.exists(local_filename): os.remove(local_filename)

    async def semantic_query(self, symbol: str, query: str, user_id: str) -> Dict[str, Any]:
        """Hybrid RAG: Retrieve chunks and synthesize with Gemini."""
        # 1. RETRIEVE
        results = self.vector_db.query(query_text=f"{symbol} {query}", n_results=10, user_id=user_id)
        context = "\n\n".join(results['documents'][0]) if results['documents'] else ""
        
        # 2. SYNTHESIZE
        return await self.broker.execute_task(
            task=query,
            provider_mode="deep", # Routing to Gemini
            raw_context=context,
            ticker=symbol
        )

    def _trigger_fallback(self, error_code: str, reason: str) -> Dict[str, Any]:
        """Signal for fault-tolerant fallback."""
        print(f"[!] [PDFIntel-Error] {error_code}: {reason}")
        return {
            "status": "FAILED_LOW_FIDELITY",
            "reason": f"[{error_code}] {reason}",
            "action": "TRIGGER_FALLBACK: RegulatorScout"
        }

if __name__ == "__main__":
    engine = PDFIntelligenceEngine()
    async def test():
        url = "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2023-24/q4/Consolidated-Financial-Results-Q4-FY2023-24.pdf"
        res = await engine.process_financial_pdf("TCS", url, user_id="test_user_123")
        print(f"Result: {res}")
    
    asyncio.run(test())
