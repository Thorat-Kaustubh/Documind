import asyncio
import time
import logging
import sys
import os
from typing import List, Dict, Any
try:
    import psutil
except ImportError:
    psutil = None

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import ExecutionOrchestrator
from database.postgres_sync import PostgresSync
from database.vector_storage import VectorStorage

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stress_test")

class BackendStressTester:
    def __init__(self):
        self.orchestrator = ExecutionOrchestrator()
        self.db = PostgresSync()
        self.vector_db = VectorStorage()
        if psutil:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None

    def get_mem_usage(self):
        if self.process:
            return self.process.memory_info().rss / (1024 * 1024)
        return 0.0

    async def test_db_concurrency(self, total_requests: int = 200):
        """Stress test Postgres audit logs with background dispatch simulation."""
        logger.info(f"--- DB DISPATCH STRESS TEST: {total_requests} entries ---")
        start_time = time.time()
        
        async def background_audit_log_sim(user_id, action, resource, ip):
            await asyncio.to_thread(self.db.create_audit_log, user_id, action, resource, ip)

        # Simulating the asyncio.create_task behavior in main.py
        tasks = []
        stress_uuid = "01234567-89ab-cdef-0123-456789abcdef"
        for i in range(total_requests):
            # This mimics the "fire-and-forget" dispatch latency
            tasks.append(asyncio.create_task(background_audit_log_sim(
                stress_uuid, "STRESS_TEST", f"index_{i}", "127.0.0.1"
            )))
        
        dispatch_duration = time.time() - start_time
        logger.info(f"Dispatch Result: {total_requests} logs queued in {dispatch_duration:.4f}s")
        
        # Wait for actual completion to measure total throughput
        await asyncio.gather(*tasks)
        total_duration = time.time() - start_time
        logger.info(f"Final DB Completion: {total_requests} logs in {total_duration:.2f}s ({total_requests/total_duration:.2f} req/s)")

    async def test_vector_db_concurrency(self, total_queries: int = 50):
        """Stress test Vector Store semantic search."""
        logger.info(f"--- VECTOR DB STRESS TEST: {total_queries} queries ---")
        start_time = time.time()
        
        queries = ["What is the market sentiment?", "Financial analysis of tech sector", "Risks in manufacturing"]
        
        async def query_one(i):
            q = queries[i % len(queries)]
            await asyncio.to_thread(self.vector_db.query, query_text=q, n_results=5, user_id="stress_test_user")

        tasks = [query_one(i) for i in range(total_queries)]
        await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        logger.info(f"Vector Result: {total_queries} queries in {duration:.2f}s ({total_queries/duration:.2f} req/s)")

    async def run_full_stress_test(self):
        logger.info(f"Starting Optimized System Stress Test. Initial Memory: {self.get_mem_usage():.2f} MB")
        
        # 1. DB Test
        await self.test_db_concurrency(200)
        logger.info(f"Memory after DB: {self.get_mem_usage():.2f} MB")
        
        # 2. Vector Test
        await self.test_vector_db_concurrency(50)
        logger.info(f"Memory after Vector: {self.get_mem_usage():.2f} MB")

if __name__ == "__main__":
    tester = BackendStressTester()
    asyncio.run(tester.run_full_stress_test())
