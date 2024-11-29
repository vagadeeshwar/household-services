# src/celeryconfig.py
from kombu import Exchange, Queue

# Broker settings
broker_url = "redis://localhost:6379/1"
result_backend = "redis://localhost:6379/2"

# Fix deprecation warning
broker_connection_retry_on_startup = True

# Timezone
timezone = "UTC"

# Task settings
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
task_default_queue = "default"

# Queue configuration
task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("reports", Exchange("reports"), routing_key="reports"),
    Queue("notifications", Exchange("notifications"), routing_key="notifications"),
)

# Route tasks to specific queues
task_routes = {
    "src.tasks.send_daily_reminders": {"queue": "notifications"},
    "src.tasks.generate_monthly_reports": {"queue": "reports"},
}

# Task execution settings
task_always_eager = False
task_acks_late = True
worker_prefetch_multiplier = 1

# Task time limits - adjusted for Windows
task_time_limit = None  # Disable hard timeout on Windows
task_soft_time_limit = None  # Disable soft timeout on Windows

# Result settings
result_expires = 3600  # 1 hour

# Logging
worker_redirect_stdouts = False
worker_redirect_stdouts_level = "INFO"

# Beat settings
beat_schedule = {
    "daily-reminders": {
        "task": "src.tasks.send_daily_reminders",
        "schedule": 60.0 * 60 * 24,  # daily
        "options": {"queue": "notifications"},
    },
    "monthly-reports": {
        "task": "src.tasks.generate_monthly_reports",
        "schedule": 60.0 * 60 * 24 * 30,  # monthly
        "options": {"queue": "reports"},
    },
}
