import redis
from src.celery_app import celery
import json


def check_redis_connection():
    """Check Redis broker and backend connections"""
    try:
        # Check broker (DB 1)
        broker = redis.Redis(host="localhost", port=6379, db=1)
        broker.ping()
        print("✅ Redis broker (DB 1) is connected")

        # Check result backend (DB 2)
        backend = redis.Redis(host="localhost", port=6379, db=2)
        backend.ping()
        print("✅ Redis result backend (DB 2) is connected")

    except Exception as e:
        print(f"❌ Redis error: {e}")


def check_task_status(task_id):
    """Check status of a specific task"""
    try:
        # Get AsyncResult
        result = celery.AsyncResult(task_id)
        print(f"\nTask Status for {task_id}:")
        print(f"Status: {result.status}")
        print(f"Ready: {result.ready()}")

        # Try to get task result from Redis directly
        r = redis.Redis(host="localhost", port=6379, db=2)
        result_key = f"celery-task-meta-{task_id}"
        raw_result = r.get(result_key)

        if raw_result:
            result_data = json.loads(raw_result)
            print("\nRaw result from Redis:")
            print(json.dumps(result_data, indent=2))
        else:
            print("\nNo result found in Redis")

    except Exception as e:
        print(f"❌ Error checking task: {e}")


def check_active_workers():
    """Check for active Celery workers"""
    try:
        i = celery.control.inspect()

        # Get active workers
        active = i.active()
        if active:
            print("\n✅ Active workers found:")
            for worker, tasks in active.items():
                print(f"Worker: {worker}")
                print(f"Active tasks: {len(tasks)}")
        else:
            print("\n❌ No active workers found!")

        # Check registered tasks
        registered = i.registered()
        if registered:
            print("\nRegistered tasks:")
            for worker, tasks in registered.items():
                print(f"\nWorker {worker} tasks:")
                for task in tasks:
                    print(f"  - {task}")

    except Exception as e:
        print(f"❌ Error checking workers: {e}")


if __name__ == "__main__":
    print("Running Celery diagnostics...\n")

    print("1. Checking Redis connections...")
    check_redis_connection()

    print("\n2. Checking workers...")
    check_active_workers()

    # Check specific task if ID provided
    task_id = input("\nEnter task ID to check (or press Enter to skip): ").strip()
    if task_id:
        check_task_status(task_id)
