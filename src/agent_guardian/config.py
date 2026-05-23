from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    OPENAI_API_KEY: str = ""
    SLACK_BOT_TOKEN: str = ""
    SLACK_CHANNEL_ID: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "sqlite:///./guardian.db"
    ALLOW_CRITICAL: bool = False
    APPROVAL_TIMEOUT: int = 300
    GUARDIAN_DEV_MODE: bool = True
    GUARDIAN_AUTO_APPROVE: bool = False
    SIMULATION_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"


settings = Settings()
