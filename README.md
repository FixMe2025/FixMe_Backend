# FixMe Backend - 맞춤법 교정 서비스

theSOL1/kogrammar-base 모델을 사용한 한국어 맞춤법 교정 FastAPI 서버

## 설치 및 실행

### 1. 의존성 설치
```bash
cd FixMe_Backend
pip install -r requirements.txt
```

### 2. 환경 설정
`.env` 파일에서 설정을 확인하거나 수정하세요:
```
MODEL_NAME=theSOL1/kogrammar-base
MAX_LENGTH=2000
CHUNK_SIZE=300
DEVICE=auto
HOST=0.0.0.0
PORT=8000
```

### 3. 서버 실행
```bash
python run.py
```

## API 엔드포인트

### 건강 상태 확인
- `GET /health`

### 맞춤법 교정
- `POST /api/v1/pipeline/run` (프론트엔드 호환)
- `POST /api/v1/comprehensive/comprehensive` (프론트엔드 호환) 
- `POST /api/v1/spellcheck`

### 요청 형식
```json
{
  "text": "교정할 텍스트"
}
```

### 응답 형식
```json
{
  "original_text": "원본 텍스트",
  "corrected_text": "교정된 텍스트", 
  "corrections": [
    {
      "original": "원본단어",
      "corrected": "교정단어",
      "type": "맞춤법/띄어쓰기"
    }
  ]
}
```

## 특징

- CUDA 우선 사용, CPU 대체
- 2000자 최대 길이 제한
- 300자 단위 청크 분할 처리
- 한글 에러 메시지
- 프론트엔드와 완전 호환