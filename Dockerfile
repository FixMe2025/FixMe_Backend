FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# PyTorch 이미지에 포함된 기본 도구 외 추가 설치
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 런타임 환경
ENV TOKENIZERS_PARALLELISM=false \
    HF_HOME=/models \
    TRANSFORMERS_CACHE=/models

COPY requirements.txt .
RUN pip install --upgrade pip
# PyTorch는 베이스 이미지에 포함되어 있으므로, requirements.txt에서 중복 설치되지 않도록 관리하는 것이 좋습니다.
RUN pip install --no-cache-dir -r requirements.txt

# 모델 캐시 디렉터리 준비
RUN mkdir -p /models

COPY app/ ./app/

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}"]
