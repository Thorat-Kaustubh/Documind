import os
import hashlib
import warnings
import logging

# --- NUCLEAR SILENCER (Absolute Production Silence) ---
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TQDM_DISABLE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
warnings.filterwarnings("ignore")
import logging
from backend.config import settings
# -----------------------------------------------------
logger = logging.getLogger("documind.vectors")

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

class VectorStorage:
    """
    Stabilized Vector Storage for ChromaDB Cloud.
    Uses explicitly requested all-MiniLM-L6-v2 (sentence-transformers) embeddings.
    ENFORCED: Zero-Emoji Policy for Windows Terminal compatibility.
    """
    def __init__(self, collection_name: str = None):
        self.host = settings.CHROMA_CLOUD_HOST
        self.api_key = settings.CHROMA_API_KEY
        self.tenant = settings.CHROMA_TENANT
        self.database = settings.CHROMA_DATABASE
        self.collection_name = collection_name or settings.CHROMA_COLLECTION
        
        # Explicit all-MiniLM-L6-v2 setup
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        try:
            # Connect via HttpClient
            self.client = chromadb.HttpClient(
                host=self.host,
                tenant=self.tenant,
                database=self.database,
                headers={"X-Chroma-Token": self.api_key}
            )
            # FIX: Explicitly check for collection to avoid the 'embedding function conflict' warning.
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name, 
                    embedding_function=self.ef
                )
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name, 
                    embedding_function=self.ef
                )
        except Exception:
            self.client = None
            self.collection = None

    def _generate_hash(self, text: str):
        return hashlib.sha256(text.encode()).hexdigest()

    def add_document(self, text: str, metadata: dict, doc_id: str):
        if not self.collection: return
        try:
            self.collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
        except Exception as e:
            logger.error(f"[Chroma-Error] Add Failed: {e}")

    def upsert_document(self, text: str, metadata: dict, namespace: str):
        if not self.collection: return None
        content_hash = self._generate_hash(text)
        doc_id = f"{namespace}_{content_hash[:16]}"
        metadata["content_hash"] = content_hash
        try:
            self.collection.upsert(documents=[text], metadatas=[metadata], ids=[doc_id])
            return doc_id
        except Exception as e:
            logger.error(f"[Chroma-Error] Operation Failed: {e}")
            return None

    def query(self, query_text: str, n_results: int = 5, user_id: str = None):
        """Secure Query with User-ID Filtering."""
        if not self.collection: return {"documents": [[]]}
        
        where_filter = {}
        if user_id:
            where_filter = {"$or": [{"user_id": user_id}, {"is_public": True}]}
        else:
            where_filter = {"is_public": True}

        try:
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
        except Exception:
            return {"documents": [[]]}

    def upsert_secure(self, text: str, metadata: dict, namespace: str, user_id: str, is_public: bool = False):
        metadata["user_id"] = user_id
        metadata["is_public"] = is_public
        return self.upsert_document(text, metadata, namespace)
