from celery import Celery
import os

# ✅ Celery Configuration (Using AWS SQS)
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "sqs://"),
    backend=None  # AWS SQS does not support result storage
)

@celery.task(name="tasks.example_task")
def example_task():
    return "Celery is working!"
