import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MODEL_NAME: str = os.getenv("MODEL_NAME", "theSOL1/kogrammar-base")
    MAX_LENGTH: int = int(os.getenv("MAX_LENGTH", "2000"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "300"))
    DEVICE: str = os.getenv("DEVICE", "auto")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
