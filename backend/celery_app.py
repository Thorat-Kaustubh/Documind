import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Use Redis as the message broker and result backend
# Default to localhost if not specified in .env
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "documind_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.tasks"] # Where our tasks are defined
)

# Optional configuration for production-grade reliability
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True, # Ensure task is acknowledged only after completion
    worker_prefetch_multiplier=1, # One task per worker for better load balancing
    task_track_started=True,
    task_time_limit=3600, # Max run time: 1 hour
    task_always_eager=False, # Use background workers
)

# CELERY BEAT: The Production-Grade Scheduler
celery_app.conf.beat_schedule = {
    "hourly-discovery-sweep": {
        "task": "tasks.discovery_sweep",
        "schedule": 3600.0, # Every hour
        "args": (["RELIANCE", "TCS", "HDFCBANK", "INFY", "NVDA", "AAPL", "TSLA"],),
    },
    "macro-heartbeat-sync": {
        "task": "tasks.macro_heartbeat_sync",
        "schedule": 600.0, # Every 10 minutes (Real-time macro heartbeat)
    },
}

if __name__ == "__main__":
    celery_app.start()
