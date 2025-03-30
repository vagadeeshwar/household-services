from celery import Celery

# Initialize Celery
celery = Celery(
    "household_services",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
    include=["src.tasks"],  # Explicitly include tasks module
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_pool_restarts=True,  # Enable worker pool restarts
    task_track_started=True,  # Track when tasks start
    task_ignore_result=False,  # Enable result backend
    worker_send_task_events=True,  # Enable task events
    task_send_sent_event=True,  # Enable sent event
)

# Load additional configurations
celery.config_from_object("src.celeryconfig")
