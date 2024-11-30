from functools import wraps
from flask import request, current_app
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


def cache_key(*args, **kwargs):
    """Generate a cache key based on request parameters"""
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return f"view/{path}-{args}"


def clear_cache_by_pattern(pattern):
    """Clear all cache entries matching a pattern"""
    if hasattr(cache, "_client"):
        # Get all keys matching the pattern
        keys = cache._client.scan_iter(match=pattern)
        # Delete all matching keys
        for key in keys:
            cache._client.delete(key)


def cached_with_auth(timeout=300):
    """A more resilient caching decorator that won't fail if Redis is unavailable"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth token for cache key
            auth_token = request.headers.get("Authorization", "")

            try:
                # Try to use the cache
                from src.utils.cache import cache

                cache_key = (
                    f"view/services/{auth_token}/{request.path}/{str(request.args)}"
                )

                # Attempt to get from cache
                cached_response = cache.get(cache_key)
                if cached_response is not None:
                    return cached_response

                # If not in cache, generate response
                response = f(*args, **kwargs)

                # Try to cache the response
                try:
                    cache.set(cache_key, response, timeout=timeout)
                except Exception as cache_error:
                    current_app.logger.warning(
                        f"Failed to set cache: {str(cache_error)}"
                    )

                return response

            except Exception as e:
                # If any cache operation fails, log and execute function normally
                current_app.logger.warning(f"Cache operation failed: {str(e)}")
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def cache_invalidate(*patterns):
    """Decorator to invalidate cache patterns after function execution"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            for pattern in patterns:
                clear_cache_by_pattern(pattern)
            return result

        return decorated_function

    return decorator
