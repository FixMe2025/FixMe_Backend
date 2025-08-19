import os
from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings


# 애플리케이션 전역 설정을 관리하는 클래스와 헬퍼 함수 정의
class Settings(BaseSettings):
    """환경 변수 기반 설정 값들을 보관하는 클래스"""
    environment: str = "development"
    log_level: str = "INFO"
    generative_model_name: str = "beomi/KoAlpaca-Polyglot-5.8B"
    secondary_model_name: str = "j5ng/et5-typos-corrector"
    grammar_model_name: str = "theSOL1/kogrammar-base"
    model_cache_dir: str = "/models"
    max_text_length: int = 2000
    use_gpu: bool = True
    
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
    """Settings 인스턴스를 생성하여 반환"""
    return Settings()

# 기본 Settings 인스턴스 생성
settings = Settings()