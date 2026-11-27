from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVars(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str

    # upstash Redis & Gmail SMTP
    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 465
    MAIL_SERVER: str
    OTP_EXPIRE_SECONDS: int = 300
    COOLDOWN_SECONDS: int = 60
    MAX_OTP_ATTEMPTS: int = 5

    # refresh token rotaion
    REFRESH_TOKEN_IDLE_DAYS: int = 7
    REFRESH_TOKEN_ABSOLUTE_DAYS: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


setting = EnvVars()
