import os
from typing import Optional
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    model_name: str = "skt/kobert-base-v1"
    model_cache_dir: str = "./models"
    max_text_length: int = 2000
    
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


settings = Settings()