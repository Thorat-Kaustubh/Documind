import chromadb
from chromadb.config import Settings
import os

class VectorStorage:
    """
    Vector Storage using ChromaDB for sentiment-aware memory.
    """
    def __init__(self, path: str = "./vector_db"):
        self.path = path
        self.client = chromadb.PersistentClient(path=self.path)
        self.collection = self.client.get_or_create_collection(name="market_intelligence")

    def add_document(self, text: str, metadata: dict, doc_id: str):
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 5):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

if __name__ == "__main__":
    storage = VectorStorage()
    # storage.add_document("Nifty 50 showing bullish trend due to tech sector growth.", {"source": "ET"}, "doc1")
    # print(storage.query("market trend"))
