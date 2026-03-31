import chromadb
import os
import hashlib
from dotenv import load_dotenv

class VectorStorage:
    """
    Stabilized Vector Storage for ChromaDB Cloud.
    Uses verified HttpClient settings for managed clusters.
    ENFORCED: Zero-Emoji Policy for Windows Terminal compatibility.
    """
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("CHROMA_CLOUD_HOST", "https://api.trychroma.com")
        self.api_key = os.getenv("CHROMA_API_KEY")
        self.tenant = os.getenv("CHROMA_TENANT")
        self.database = os.getenv("CHROMA_DATABASE")
        self.collection_name = os.getenv("CHROMA_COLLECTION", "market_intelligence")
        
        try:
            # Connect via HttpClient
            self.client = chromadb.HttpClient(
                host=self.host,
                tenant=self.tenant,
                database=self.database,
                headers={"X-Chroma-Token": self.api_key}
            )
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            print(f"[VectorStorage] Connected to Cloud Collection: {self.collection_name}")
        except Exception as e:
            print(f"[VectorStorage] Warning: {e}")
            self.client = None
            self.collection = None

    def _generate_hash(self, text: str):
        return hashlib.sha256(text.encode()).hexdigest()

    def add_document(self, text: str, metadata: dict, doc_id: str):
        if not self.collection: return
        try:
            self.collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
        except Exception as e:
            print(f"[Chroma-Error] Add Failed: {e}")

    def upsert_document(self, text: str, metadata: dict, namespace: str):
        if not self.collection: return
        content_hash = self._generate_hash(text)
        doc_id = f"{namespace}_{content_hash[:16]}"
        metadata["content_hash"] = content_hash
        try:
            self.collection.upsert(documents=[text], metadatas=[metadata], ids=[doc_id])
            return True
        except Exception as e:
            print(f"[Chroma-Error] Upsert Failed: {e}")
            return False

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
        except Exception as e:
            print(f"[Chroma-Error] Query Failed: {e}")
            return {"documents": [[]]}

    def upsert_secure(self, text: str, metadata: dict, namespace: str, user_id: str, is_public: bool = False):
        metadata["user_id"] = user_id
        metadata["is_public"] = is_public
        return self.upsert_document(text, metadata, namespace)
