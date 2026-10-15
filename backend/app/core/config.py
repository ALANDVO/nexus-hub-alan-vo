from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "nexus-hub"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+psycopg2://nexus:nexus@db:5432/nexus"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Keycloak / OIDC
    keycloak_url: str = "http://keycloak:8080"
    keycloak_realm: str = "nexus"
    keycloak_client_id: str = "nexus-backend"
    keycloak_client_secret: Optional[str] = None
    oidc_issuer: Optional[str] = None
    oidc_audience: str = "nexus-api"
    oidc_jwks_cache_ttl: int = 300

    # LLM
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    llm_timeout: float = 30.0

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    hnsw_index_path: str = "/data/hnsw_index"

    # Security
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:5173", "http://frontend:5173"]

    # Demo mode
    demo_mode: bool = False
    demo_bind_host: str = "127.0.0.1"


@lru_cache
def get_settings() -> Settings:
    return Settings()