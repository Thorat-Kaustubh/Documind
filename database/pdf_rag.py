import os
import requests
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.vector_storage import VectorStorage

class PDFIntelligenceEngine:
    """
    RAG Engine for Financial Documents.
    Downloads -> Chunks -> Embeds -> Stores in ChromaDB Cloud.
    """
    def __init__(self):
        self.vector_db = VectorStorage()
        self.temp_dir = "temp_pdfs"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_financial_pdf(self, symbol: str, pdf_url: str, is_local: bool = False):
        """
        Full pipeline to ingest a PDF. Handles both web URLs and local uploads.
        """
        try:
            local_filename = pdf_url if is_local else os.path.join(self.temp_dir, f"{symbol}_current.pdf")
            
            if not is_local:
                print(f"📥 Downloading PDF for {symbol}: {pdf_url}")
                # Fault Tolerant Download
                for attempt in range(3):
                    try:
                        response = requests.get(pdf_url, stream=True, timeout=15)
                        if response.status_code == 200:
                            with open(local_filename, 'wb') as f:
                                f.write(response.content)
                            break
                    except Exception as e:
                        if attempt == 2: raise e
                        print(f"⚠️ Retry {attempt+1} for {symbol} PDF...")
                        time.sleep(1)

            # Load and Split
            loader = PyPDFLoader(local_filename)
            docs = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            splits = text_splitter.split_documents(docs)

            # Store in Chroma Cloud: Batch Processing
            print(f"🧠 Batch Indexing {len(splits)} chunks for {symbol}...")
            source_key = os.path.basename(local_filename)
            
            batch_texts, batch_metas, batch_ns = [], [], []
            
            for i, split in enumerate(splits):
                batch_texts.append(split.page_content)
                batch_metas.append({
                    "symbol": symbol, 
                    "source": source_key, 
                    "page": split.metadata.get("page", 0)
                })
                batch_ns.append(f"{symbol}_{source_key}_{i}")

                # Flush in chunks of 25 to optimize network request size
                if len(batch_texts) >= 25:
                    self.vector_db.upsert_batch(batch_texts, batch_metas, batch_ns)
                    batch_texts, batch_metas, batch_ns = [], [], []
            
            # Final flush
            if batch_texts:
                self.vector_db.upsert_batch(batch_texts, batch_metas, batch_ns)
            
            print(f"✅ PDF RAG ready for {symbol}")
            return True
        except Exception as e:
            print(f"❌ PDF Processing failed: {e}")
            return False
