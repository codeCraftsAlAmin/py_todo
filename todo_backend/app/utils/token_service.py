import hashlib
import hmac
import time

from ..config.redis import redis_client
from ..config.settings import setting

secret_key = setting.SECRET_KEY
refresh_token_idle_days = (
    setting.REFRESH_TOKEN_IDLE_DAYS
)  # session will be expired if it has been inactive for 7 day
refresh_token_absolute_days = (
    setting.REFRESH_TOKEN_ABSOLUTE_DAYS
)  # have to re-login after 30days


def hash_token(raw_token: str) -> str:
    return hmac.new(
        key=secret_key.encode(), msg=raw_token.encode(), digestmod=hashlib.sha256
    ).hexdigest()


# atomic Token rotation, concurrency guard, reuse detection & dual expiry `Lua Script`
ROTATE_TOKEN_FAMILY_LUA = """
local family_key = KEYS[1]
local used_key = KEYS[2]
local user_families_key = KEYS[3]

local submitted_hash = ARGV[1]
local new_hash = ARGV[2]
local now_ts = tonumber(ARGV[3])
local idle_ttl = tonumber(ARGV[4])
local family_id = ARGV[5]

-- 1. check family exists or not(logout if not)
if redis.call('EXISTS', family_key) == 0 then
    redis.call('SREM', user_families_key, family_id)
    return {'EXPIRED', 0}
end

local status = redis.call('HGET', family_key, 'status')
local current_hash = redis.call('HGET', family_key, 'current_hash')
local abs_exp = tonumber(redis.call('HGET', family_key, 'abs_exp')or '0')

-- 2. family already logged out or not
if status ~= 'active' then
    return {'REVOKED', 0}
end

-- 3. check absolute expiration
if now_ts >= abs_exp then
    redis.call('DEL', family_key)
    redis.call('SREM', user_families_key, family_id)
    return {'ABSOLUTE_EXPIRED', 0}
end

-- 4. token reuse detection, if yes then revoke the token family and shut down the session 
if redis.call('EXISTS', used_key) == 1 then
    redis.call('HSET', family_key, 'status', 'revoked')
    redis.call('DEL', family_key)
    redis.call('SREM', user_families_key, family_id)
    return {'REUSE_DETECTED', 0}
end

-- 5. check current token hash
if current_hash ~= submitted_hash then
    return {'INVALID', 0}
end 

-- 6. determinig effective ttl: min(idle_ttl, remaining_absolute_ttl)
local remaining_abs = abs_exp - now_ts
local effective_ttl = idle_ttl

if remaining_abs < idle_ttl then
    effective_ttl = remaining_abs
end

-- 7. atomic roation
-- maked old hashed token as 'used'
redis.call('SETEX', used_key, remaining_abs, 'used')

-- set new token hased as 'current_hash' and reset 'idl ttl'
redis.call('HSET', family_key, 'current_hash', new_hash)
redis.call('EXPIRE', family_key, effective_ttl)

local current_index_ttl = redis.call('TTL', user_families_key)
if current_index_ttl < remaining_abs then
    redis.call('EXPIRE', user_families_key, remaining_abs)
end

return {'ROTATED', effective_ttl}
"""

rotate_family_script = redis_client.register_script(ROTATE_TOKEN_FAMILY_LUA)


# create new `token family` for new login and returns effective ttl
async def create_token_family(
    user_id: str, family_id: str, raw_refresh_token: str
) -> int:
    now_ts = int(time.time())
    idle_ttl = refresh_token_idle_days * 24 * 60 * 60
    abs_ttl = refresh_token_absolute_days * 24 * 60 * 60
    abs_exp = now_ts + abs_ttl

    current_hash = hash_token(raw_token=raw_refresh_token)
    family_key = f"rt:family:{family_id}"
    user_families_key = f"user:families:{user_id}"

    pipe = redis_client.pipeline()
    pipe.hset(
        family_key,
        mapping={
            "user_id": user_id,
            "current_hash": current_hash,
            "status": "active",
            "abs_exp": abs_exp,
        },
    )
    pipe.expire(family_key, idle_ttl)
    pipe.sadd(user_families_key, family_id)
    pipe.expire(user_families_key, abs_ttl)
    await pipe.execute()

    return idle_ttl


# rotate token atomically and handles `Reuse/Concurrency/Expiry`
async def rotate_family_token(
    user_id: str,
    family_id: str,
    submitted_raw_token: str,
    new_raw_token: str,
) -> tuple[bool, str, int]:
    now_ts = int(time.time())
    idle_ttl = refresh_token_idle_days * 24 * 60 * 60

    submitted_hash = hash_token(raw_token=submitted_raw_token)
    new_hash = hash_token(raw_token=new_raw_token)

    family_key = f"rt:family:{family_id}"
    used_key = f"rt:used:{family_id}:{submitted_hash}"
    user_families_key = f"user:families:{user_id}"

    status_code, effective_ttl = await rotate_family_script(
        keys=[family_key, used_key, user_families_key],
        args=[submitted_hash, new_hash, now_ts, idle_ttl, family_id],
    )

    if status_code == "ROTATED":
        return True, "Token rotated successfully.", int(effective_ttl)
    if status_code == "REUSE_DETECTED":
        return (
            False,
            "Token reuse detected. Security breach suspected—session revoked.",
            0,
        )
    if status_code == "ABSOLUTE_EXPIRED":
        return False, "Maximum session lifetime reached. Please log in again.", 0
    return False, "Session expired or invalid. Please log in again.", 0


# logout from a single device
async def revoke_single_device(user_id: str, family_id: str) -> None:
    used_keys = [key async for key in redis_client.scan_iter(f"rt:used:{family_id}:*")]
    pipe = redis_client.pipeline()
    pipe.delete(f"rt:family:{family_id}")

    if used_keys:
        pipe.delete(*used_keys)
    pipe.srem(f"user:families:{user_id}", family_id)
    await pipe.execute()


# logout from all devices
async def revoke_all_devices(user_id: str) -> None:
    user_families_key = f"user:families:{user_id}"
    family_ids = await redis_client.smembers(user_families_key)

    pipe = redis_client.pipeline()
    for fid in family_ids:
        pipe.delete(f"rt:family:{fid}")
        async for used_key in redis_client.scan_iter(f"rt:used:{fid}:*"):
            pipe.delete(used_key)
    pipe.delete(user_families_key)
    await pipe.execute()
