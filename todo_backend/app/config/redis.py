from redis.asyncio import Redis

from ..config.settings import setting

redis_url = setting.REDIS_URL
redis_client = Redis.from_url(redis_url, decode_responses=True)
