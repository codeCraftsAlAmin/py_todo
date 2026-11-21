import hashlib
import secrets

from redis.asyncio import Redis

from ..config.settings import setting

redis_url = setting.REDIS_URL
otp_expire_sec = setting.OTP_EXPIRE_SECONDS  # 5min
cooldown_sec = setting.COOLDOWN_SECONDS  # can't resend before 60s
max_otp_attempts = setting.MAX_OTP_ATTEMPTS  # max 5times wrong attempts are allowed
secret_key = setting.SECRET_KEY

# 100% atomic OTP Verification & Brute-Force Protection Lua Script
VERIFY_OTP_LUA = """
local otp_key = KEYS[1]
local attempts_key = KEYS[2]
local submitted_hash = ARGV[1]
local max_attempts = tonumber(ARGV[2])

local stored_hashed = redis.call('GET', otp_key)
if not stored_hashed then
    return {'EXPIRED',0}
end

local attemts = tonumber(redis.call('GET', attempts_key) or '0')
if attemts >= max_attempts then
    redis.call('DEL', otp_key, attempts_key)
    return {'LOCKED', 0}
end

if stored_hashed == submitted_hash then
    redis.call('DEL', otp_key, attempts_key)
    return {'VALID', 0}
else
    local new_attempts = redis.call('INCR', attempts_key)
    if new_attempts >= max_attempts then
        redis.call('DEL', otp_key, attempts_key)
        return {'LOCKED', 0}
    end
    return {'INVALID', max_attempts - new_attempts}
end
"""

redis_client = Redis.from_url(redis_url, decode_responses=True)

verify_otp_script = redis_client.register_script(VERIFY_OTP_LUA)


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(f"{otp}{secret_key}".encode()).hexdigest()


async def is_resend_allowed(email: str) -> tuple[bool, int]:
    cooldown_key = f"otp:cooldown:{email.lower()}"
    ttl = await redis_client.ttl(cooldown_key)
    if ttl <= 0:  # -2 (key doesn't exist), -1 (no expiry), or 0 (just expired)
        return True, 0
    return False, max(ttl, 0)


async def save_otp(email: str, otp: str) -> None:
    normalized_email = email.lower()
    otp_key = f"otp:verify:{normalized_email}"
    attempts_key = f"otp:attempts:{normalized_email}"
    cooldown_key = f"otp:cooldown:{normalized_email}"

    pipe = redis_client.pipeline()
    pipe.setex(otp_key, otp_expire_sec, _hash_otp(otp))
    pipe.setex(attempts_key, otp_expire_sec, 0)
    pipe.setex(cooldown_key, cooldown_sec, "1")
    await pipe.execute()


async def verify_otp(email: str, submitted_otp: str) -> tuple[bool, str]:
    # execute the redis lua script to verify the otp automatically
    normalized_email = email.lower()
    otp_key = f"otp:verify:{normalized_email}"
    attempts_key = f"otp:attempts:{normalized_email}"

    status_code, remaining = await verify_otp_script(
        keys=[otp_key, attempts_key], args=[_hash_otp(submitted_otp), max_otp_attempts]
    )

    if status_code == "VALID":
        return True, "OTP verified successfully."
    if status_code == "EXPIRED":
        return False, "OTP has expired or does not exist. Please request a new one."
    if status_code == "LOCKED":
        return False, "Too many failed attempts, OTP invalidated."
    return False, f"Invalid OTP, {remaining} attempt(s) remaining."
