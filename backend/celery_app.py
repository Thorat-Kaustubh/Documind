import os
from celery import Celery
from celery.schedules import crontab
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
        "schedule": 600.0, # Every 10 minutes
    },
    "ipo-scouting-pulse": {
        "task": "tasks.ipo_discovery",
        "schedule": 43200.0, # Every 12 hours
    },
    "mutual-fund-monitoring": {
        "task": "tasks.mutual_fund_sync",
        "schedule": 86400.0, # Every 24 hours
        "args": (["0P0000XW01.BO", "0P0000XW01.BO"],), # Sample MF symbols
    },
    "banking-sector-scout": {
        "task": "tasks.sector_discovery",
        "schedule": 86400.0,
        "args": ("Banking",),
    },
    "tech-sector-scout": {
        "task": "tasks.sector_discovery",
        "schedule": 86400.0,
        "args": ("Technology",),
    },
    "green-energy-scout": {
        "task": "tasks.sector_discovery",
        "schedule": 86400.0,
        "args": ("Renewable Energy",),
    },
    "sentiment-trigger-monitor": {
        "task": "tasks.sentiment_trigger_engine",
        "schedule": 900.0, # Every 15 minutes
    },
    "daily-regulatory-scout": {
        "task": "tasks.regulatory_scout",
        # Runs every day at 18:00 UTC (around market close)
        "schedule": crontab(hour=18, minute=0),
        "args": ("RELIANCE",),
    },
    "daily-financial-scan": {
        "task": "tasks.deep_financial_scan",
        # Runs every day at 02:00 UTC (off-peak hours)
        "schedule": crontab(hour=2, minute=0),
        "args": ("RELIANCE",),
    },
}

if __name__ == "__main__":
    celery_app.start()
