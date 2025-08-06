import os
from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    generative_model_name: str = "beomi/KoAlpaca-Polyglot-5.8B"
    secondary_model_name: str = "j5ng/et5-typos-corrector"
    model_cache_dir: str = "/models"
    max_text_length: int = 1500
    use_gpu: bool = False
    
    # FastAPI 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # CORS 설정
    allowed_origins: str = "*"
    allow_credentials: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        protected_namespaces = ()


def get_settings() -> Settings:
    return Settings()

settings = Settings()