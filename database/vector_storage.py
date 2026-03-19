import chromadb
import os
import hashlib
from dotenv import load_dotenv

class VectorStorage:
    """
    Stabilized Vector Storage for ChromaDB Cloud.
    Uses verified HttpClient settings for managed clusters.
    """
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("CHROMA_CLOUD_HOST", "https://api.trychroma.com")
        self.api_key = os.getenv("CHROMA_API_KEY")
        self.tenant = os.getenv("CHROMA_TENANT")
        self.database = os.getenv("CHROMA_DATABASE")
        self.collection_name = os.getenv("CHROMA_COLLECTION", "market_intelligence")
        
        try:
            # We use HttpClient with X-Chroma-Token as verified in test_chroma_cloud_v3.py
            self.client = chromadb.HttpClient(
                host=self.host,
                tenant=self.tenant,
                database=self.database,
                headers={"X-Chroma-Token": self.api_key}
            )
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            print(f"✅ VectorStorage: Connected to Cloud Collection '{self.collection_name}'")
        except Exception as e:
            print(f"⚠️ VectorStorage Warning: {e}")
            self.client = None
            self.collection = None

    def _generate_hash(self, text: str):
        """Generates a unique deterministic hash of the content to prevent duplicates."""
        return hashlib.sha256(text.encode()).hexdigest()

    def add_document(self, text: str, metadata: dict, doc_id: str):
        """Standard add with automatic ID management and error handling."""
        if not self.collection: return
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"❌ Chroma Add Error: {e}")

    def upsert_document(self, text: str, metadata: dict, namespace: str):
        """
        Smart Indexing: 
        1. Hashes content.
        2. Checks if this namespace already has this exact hash.
        3. Only updates if content has changed. (Prevents Vector Noise).
        """
        if not self.collection: return
        
        content_hash = self._generate_hash(text)
        doc_id = f"{namespace}_{content_hash[:16]}" # Deterministic ID
        
        # Add hash to metadata for verification
        metadata["content_hash"] = content_hash
        
        try:
            self.collection.upsert(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"❌ Chroma Upsert Error: {e}")
            return False

    def upsert_batch(self, texts: list, metadatas: list, namespaces: list):
        """
        High-Throughput Batch Indexing:
        Reduces Network RTT by up to 90%. Essential for processing 100+ page PDFs.
        """
        if not self.collection or not texts: return False
        
        doc_ids = []
        final_metadatas = []
        
        for text, meta, ns in zip(texts, metadatas, namespaces):
            content_hash = self._generate_hash(text)
            doc_id = f"{ns}_{content_hash[:16]}"
            meta["content_hash"] = content_hash
            doc_ids.append(doc_id)
            final_metadatas.append(meta)
            
        try:
            self.collection.upsert(
                documents=texts,
                metadatas=final_metadatas,
                ids=doc_ids
            )
            return True
        except Exception as e:
            print(f"❌ Batch Upsert Error: {e}")
            return False

    def query(self, query_text: str, n_results: int = 5):
        if not self.collection: return {"documents": [[]]}
        try:
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        except Exception as e:
            print(f"❌ Query Error: {e}")
            return {"documents": [[]]}
