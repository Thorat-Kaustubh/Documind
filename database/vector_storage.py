import chromadb
import os
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

    def add_document(self, text: str, metadata: dict, doc_id: str):
        if not self.collection: return
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 5):
        if not self.collection: return {"documents": [[]]}
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
