from fastapi import Request

from ..config.exceptions import RateLimitExceededError
from ..config.redis import redis_client

RATE_LIMIT_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


def get_client_ip(request: Request) -> str:
    forward_for = request.headers.get("X-Forwarded-For")

    if forward_for:
        return forward_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limiter(max_req: int, window_sec: int):
    async def dependency(request: Request) -> None:
        client_ip = get_client_ip(request)
        route_path = request.url.path
        key = f"rate_limit:{route_path}:{client_ip}"

        current_count, ttl = await redis_client.eval(RATE_LIMIT_LUA, 1, key, window_sec)

        if int(current_count) > max_req:
            retry_after = max(int(ttl), 1)
            raise RateLimitExceededError(retry_after=retry_after)

    return dependency
