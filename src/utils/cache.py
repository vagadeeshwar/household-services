import hashlib
from functools import wraps

from flask import current_app, request
from flask_caching import Cache

# Initialize cache
cache = Cache()


def init_cache(app):
    """Initialize Redis cache with app configuration"""
    cache_config = {
        "CACHE_TYPE": "redis",
        "CACHE_REDIS_URL": "redis://localhost:6379/0",
        "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes default
    }
    app.config.update(cache_config)
    cache.init_app(app)


def get_cache_key(path, args_str, kwargs_str, user_id=None):
    """Generate a consistent cache key"""
    if user_id:
        # Auth context - include user_id
        key_string = f"user:{user_id}:{path}:{args_str}:{kwargs_str}"
        return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    else:
        # Non-auth context
        key_string = f"{path}:{args_str}:{kwargs_str}"
        return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"


def cache_(timeout=300):
    """
    Unified cache decorator that handles both authenticated and non-authenticated contexts.

    Args:
        timeout: Cache expiration time in seconds
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine if we're in an auth context by checking first arg
            user_id = None
            is_auth_context = args and hasattr(args[0], "id")

            if is_auth_context:
                user_id = args[0].id

            # Get request-specific components for the cache key
            path = request.path
            args_str = request.query_string.decode("utf-8")
            kwargs_str = str(kwargs)

            # Generate cache key
            cache_key = get_cache_key(path, args_str, kwargs_str, user_id)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # If not in cache, execute the function
            result = f(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, timeout=timeout)

            # If auth context, map this key to the user for later invalidation
            if is_auth_context:
                try:
                    import redis

                    user_cache_set_key = f"user_cache_keys:{user_id}"

                    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

                    pipe = redis_client.pipeline()
                    pipe.sadd(user_cache_set_key, cache_key)
                    pipe.expire(user_cache_set_key, timeout)
                    pipe.execute()
                except Exception as e:
                    current_app.logger.warning(f"Cache mapping failed: {str(e)}")

            return result

        return decorated_function

    return decorator


def cache_invalidate(user_id=None):
    """
    Invalidate cache - either for a specific user or the entire cache
    """
    try:
        # Use Flask-Caching's built-in clear method
        cache.clear()
        return True
    except Exception as e:
        current_app.logger.error(f"Error invalidating cache: {str(e)}")
        return False
