# FixMe Backend

FixMe 프로젝트의 한국어 맞춤법 및 문체 교정 API 서버입니다. FastAPI를 기반으로 구축되었으며, Hugging Face Transformers와 LangGraph를 사용하여 텍스트 교정 서비스를 제공합니다.

## ✨ 주요 기능

- **맞춤법 및 띄어쓰기 교정**: 기본적인 한국어 맞춤법과 띄어쓰기 오류를 교정합니다.
- **종합 교정 및 문체 변환**: 맞춤법 교정뿐만 아니라, 사용자가 선택한 대상 문체(예: 격식체, 블로그체)에 맞게 텍스트를 변환합니다.
- **GPU 가속**: PyTorch 및 `accelerate` 라이브러리를 통해 CUDA GPU 가속을 지원하며, GPU가 없을 경우 CPU로 자동 전환됩니다.
- **긴 텍스트 처리**: 긴 텍스트를 효율적으로 처리하기 위해 내부적으로 텍스트를 청크 단위로 분할하여 처리합니다.
- **컨테이너 지원**: Docker를 통해 간편하게 서버를 빌드하고 배포할 수 있습니다.

## 🛠️ 기술 스택

- **언어**: Python 3.12+
- **프레임워크**: FastAPI
- **AI/ML**:
  - Hugging Face Transformers
  - PyTorch
  - LangGraph
- **배포**: Uvicorn, Docker

## 🚀 설치 및 실행

### 1. 저장소 복제 및 가상환경 설정

```bash
git clone <저장소_URL>
cd FixMe_Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`example.env` 파일을 복사하여 `.env` 파일을 생성하고, 필요에 따라 설정을 수정합니다.

```bash
cp example.env .env
```

**.env 파일 예시:**
```
# 모델 및 처리 설정
MODEL_NAME=theSOL1/kogrammar-base
MAX_LENGTH=2000
CHUNK_SIZE=300

# 서버 설정
DEVICE=auto  # 'cuda', 'cpu', 'auto' 중 선택
HOST=0.0.0.0
PORT=8000
```

### 4. 서버 실행

#### 로컬 개발 서버

```bash
python run.py
```
서버는 `http://localhost:8000`에서 실행됩니다.

#### Docker 사용

```bash
docker-compose up --build -d
```
Docker 컨테이너가 백그라운드에서 실행됩니다.

## 📖 API 엔드포인트

API 문서는 서버 실행 후 `http://localhost:8000/docs`에서 확인할 수 있습니다.

---

### `GET /health`

서버의 상태와 모델 로딩 여부를 확인합니다.

- **응답 (성공 시)**:
  ```json
  {
    "status": "healthy",
    "is_model_loaded": true,
    "device": "cuda"
  }
  ```

---

### `POST /api/v1/pipeline/run`

기본적인 맞춤법 및 띄어쓰기 교정을 수행합니다. (프론트엔드 호환)

- **요청 본문**:
  ```json
  {
    "text": "아버지가방에들어가신다"
  }
  ```
- **응답 본문**:
  ```json
  {
    "original_text": "아버지가방에들어가신다",
    "corrected_text": "아버지가 방에 들어가신다",
    "corrections": [
      {
        "original": "아버지가방에들어가신다",
        "corrected": "아버지가 방에 들어가신다",
        "type": "띄어쓰기"
      }
    ],
    "suggestions": []
  }
  ```

---

### `POST /api/v1/comprehensive/comprehensive`

맞춤법 교정과 함께 지정된 문체로 변환하는 종합 교정을 수행합니다.

- **요청 본문**:
  ```json
  {
    "text": "이거 정말 대박이에요. 꼭 한번 써보세요.",
    "target_style": "formal"
  }
  ```
- **응답 본문**:
  ```json
  {
    "original_text": "이거 정말 대박이에요. 꼭 한번 써보세요.",
    "corrected_text": "이것은 정말 훌륭합니다. 꼭 한번 사용해 보십시오.",
    "styled_text": "이것은 정말 훌륭합니다. 꼭 한번 사용해 보십시오.",
    "target_style": "formal",
    "spellcheck_corrections": [
        {
            "original": "대박이에요",
            "corrected": "훌륭합니다",
            "type": "맞춤법"
        }
    ],
    "style_suggestions": [],
    "available_styles": ["formal", "informal", "blog"],
    "style_applied": true,
    "improvements_made": []
  }
  ```

---

### `GET /api/v1/comprehensive/styles`

사용 가능한 문체 스타일 목록을 조회합니다.

- **응답 본문**:
  ```json
  [
    {
      "name": "formal",
      "description": "격식적이고 공적인 상황에 어울리는 문체입니다.",
      "example_transforms": {
        "original": "이거 진짜 좋아요.",
        "transformed": "이것은 정말 좋습니다."
      }
    },
    {
      "name": "blog",
      "description": "친근하고 부드러운 블로그 포스팅 스타일의 문체입니다.",
      "example_transforms": {
        "original": "이거 진짜 좋아요.",
        "transformed": "이거 진짜 좋은 것 같아요! 😄"
      }
    }
  ]
  ```

## ✅ 테스트

프로젝트의 테스트를 실행하려면 다음 명령어를 사용하세요.

```bash
pytest tests/
```
