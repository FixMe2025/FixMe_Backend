import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # [기존 모델 - 되돌리려면 아래 주석 해제]
    # MODEL_NAME: str = os.getenv("MODEL_NAME", "theSOL1/kogrammar-base")

    # [현재 사용 모델 - KoGEC 600M (가벼운 버전, CPU 호환)]
    MODEL_NAME: str = os.getenv("MODEL_NAME", "sionic-ai/nllb-200-ko-gec-600M")

    # [고성능 모델 - GPU 8GB 이상 필요]
    # MODEL_NAME: str = os.getenv("MODEL_NAME", "sionic-ai/nllb-200-ko-gec-3.3B")
    MAX_LENGTH: int = int(os.getenv("MAX_LENGTH", "2000"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "300"))
    DEVICE: str = os.getenv("DEVICE", "auto")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
