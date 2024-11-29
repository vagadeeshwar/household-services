from functools import wraps
from flask import request
from flask_caching import Cache
import hashlib

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


# Cache decorators
def cached_with_auth(timeout=300):
    """Cache decorator that includes user authentication in cache key"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth token from request
            auth_token = request.headers.get("Authorization", "")

            # Create unique cache key including auth info
            key_parts = [
                request.path,
                str(hash(frozenset(request.args.items()))),
                hashlib.md5(auth_token.encode()).hexdigest(),
            ]
            cache_key = "view/" + "-".join(key_parts)

            # Try to get response from cache
            rv = cache.get(cache_key)
            if rv is not None:
                return rv

            # If not in cache, generate response and cache it
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv

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
