from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="XLAB_", env_file=".env", extra="ignore")

    api_key: str = "change-me"
    db_path: str = "xlab.db"
    retention_days: int = 30
    default_region: str = "ZA"
    hibp_key: str = ""
    ipinfo_token: str = ""
    wmn_max_sites: int = 400
    wmn_cache: str = ".cache/wmn-data.json"
    http_timeout: float = 12.0
    concurrency: int = 20
    user_agent: str = "X-Lab-KYC/0.1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
