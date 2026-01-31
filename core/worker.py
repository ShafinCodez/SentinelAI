from celery import Celery
import os

redis_host = os.getenv("REDIS_HOST", "redis")
celery_app = Celery(
    "sentinel_worker",
    broker=f"redis://{redis_host}:6379/0",
    backend=f"redis://{redis_host}:6379/0"
)

celery_app.conf.task_routes = {
    "engine.tasks.run_sast_scan": "sast",
    "engine.tasks.enrich_finding": "llm",
}
