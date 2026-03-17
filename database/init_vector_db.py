import os
import chromadb
from dotenv import load_dotenv

def setup_vector_db():
    load_dotenv()
    print("🚀 Initializing ChromaDB Cloud Architecture...")
    
    cloud_host = os.getenv("CHROMA_CLOUD_HOST", "https://api.trychroma.com")
    tenant = os.getenv("CHROMA_TENANT")
    database = os.getenv("CHROMA_DATABASE")
    api_key = os.getenv("CHROMA_API_KEY")
    collection_name = os.getenv("CHROMA_COLLECTION", "market_intelligence")

    try:
        print(f"Connecting to Cloud: {cloud_host}")
        print(f"Tenant: {tenant} | Database: {database}")
        
        client = chromadb.HttpClient(
            host=cloud_host,
            tenant=tenant,
            database=database,
            headers={"X-Chroma-Token": api_key}
        )

        # Heartbeat check
        hb = client.heartbeat()
        print(f"✅ Heartbeat: {hb}")

        # Create Core Project Collections
        collections = [
            {"name": "market_intelligence", "metadata": {"hnsw:space": "cosine"}},
            {"name": "research_history", "metadata": {"hnsw:space": "cosine"}}
        ]

        for coll in collections:
            c = client.get_or_create_collection(
                name=coll["name"],
                metadata=coll["metadata"]
            )
            print(f"✅ Collection Ready: {c.name}")
        
        return client
    except Exception as e:
        print(f"❌ Initialization Failed: {e}")
        return None

if __name__ == "__main__":
    setup_vector_db()
