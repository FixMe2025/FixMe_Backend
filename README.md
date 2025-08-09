# FixMe - 한글 맞춤법 교정 API

FixMe는 FastAPI를 기반으로 구축된 한글 맞춤법 교정 및 문장 개선 API 서비스입니다. 이 서비스는 다양한 최신 AI 모델을 활용하여 사용자에게 여러 수준의 텍스트 교정 기능을 제공합니다.

- **종합 검사 서비스**: `beomi/KoAlpaca-Polyglot-5.8B` 모델을 중심으로 `j5ng/et5-typos-corrector`를 보조로 사용하여 맞춤법, 띄어쓰기, 문장 개선을 한 번에 수행합니다.
- **LangGraph 파이프라인**: `j5ng/et5-typos-corrector`로 1차 교정 후, `theSOL1/kogrammar-base` 모델로 2차 문법 및 자연스러움을 교정하는 정교한 파이프라인을 제공합니다.

## ✨ 주요 기능

- **종합 텍스트 검사**: 맞춤법, 타이포, 문장 개선을 한 번에 처리하여 최적의 결과를 제공합니다.
- **LangGraph 파이프라인**: 2단계 모델 파이프라인을 통해 더 정확하고 자연스러운 문장을 생성합니다.
- **상세한 교정 정보**: 각 오류에 대해 원본, 교정 내용, 오류 유형을 반환하여 사용자가 오류를 명확하게 이해하도록 돕습니다.
- **유연한 API**: 필요에 따라 종합 검사, 맞춤법만, 또는 문장 개선만 선택적으로 사용할 수 있습니다.
- **상태 확인 및 서비스 정보**: 각 서비스의 상태와 사용 중인 모델 정보를 확인할 수 있는 엔드포인트를 제공합니다.

## 🏛️ 아키텍처

FixMe 백엔드는 두 가지 주요 서비스 흐름을 가집니다.

1.  **통합 서비스 (Integrated Service)**: `comprehensive`, `spellcheck`, `improvement` 엔드포인트를 담당합니다. `IntegratedCorrectionService`가 `ThreadPoolExecutor`를 사용해 여러 모델(`KoAlpaca`, `et5-typos-corrector`)을 병렬로 호출하여 빠른 응답을 제공합니다.
2.  **LangGraph 파이프라인**: `pipeline` 엔드포인트를 담당합니다. `LangGraph`를 사용하여 `et5-typos-corrector` (1차 교정)와 `kogrammar-base` (2차 교정) 모델을 순차적으로 실행하는 워크플로우를 구성하여, 더 깊이 있는 교정을 수행합니다.

## 🛠️ 기술 스택

- **언어:** Python 3.11
- **프레임워크:** FastAPI, LangGraph
- **AI 모델:**
  - `beomi/KoAlpaca-Polyglot-5.8B` (주요 생성형 모델)
  - `j5ng/et5-typos-corrector` (타이포/띄어쓰기 교정)
  - `theSOL1/kogrammar-base` (문법/자연스러움 교정)
- **라이브러리:** Transformers, PyTorch, Uvicorn
- **컨테이너:** Docker

## API 엔드포인트

| Method | Endpoint                               | 설명                                         |
| ------ | -------------------------------------- | -------------------------------------------- |
| POST   | `/api/v1/comprehensive/comprehensive`  | 맞춤법, 타이포, 문장 개선을 종합적으로 수행합니다. |
| POST   | `/api/v1/pipeline/run`                 | LangGraph 파이프라인을 통해 텍스트를 교정합니다. |
| GET    | `/api/v1/comprehensive/health`         | 종합 서비스의 모든 모델 상태를 확인합니다.   |
| GET    | `/api/v1/pipeline/health`              | LangGraph 파이프라인의 상태를 확인합니다.    |
| GET    | `/health`                              | API 서버의 기본 상태를 확인합니다.           |

### 종합 검사 (`/api/v1/comprehensive/comprehensive`)

- **Request Body:**

```json
{
  "text": "사용자가 입력한 텍스트입니다.",
  "include_improvement": true,
  "style": "formal"
}
```

- **Response Body:**

```json
{
  "original_text": "원본 텍스트",
  "corrected_text": "교정된 텍스트",
  "corrections": [
    {
      "original": "오류 단어",
      "corrected": "교정 단어",
      "type": "오류 유형"
    }
  ],
  "improvements": {
    "original_text": "교정된 텍스트",
    "improved_text": "개선된 문장",
    "suggestions": [
        {"text": "개선 제안 1", "confidence": 0.9},
        {"text": "개선 제안 2", "confidence": 0.85}
    ],
    "style_applied": "formal"
  },
  "has_errors": true,
  "total_corrections": 1,
  "status": "success",
  "message": "종합 검사가 완료되었습니다. 1개의 교정사항을 발견했습니다."
}
```

### LangGraph 파이프라인 (`/api/v1/pipeline/run`)

- **Request Body:**

```json
{
  "text": "안녕 하세요 저녁 머거요"
}
```

- **Response Body:**

```json
{
    "original_text": "안녕 하세요 저녁 머거요",
    "corrected_text": "안녕하세요, 저녁 먹어요.",
    "corrections": [
        {
            "original": "안녕 하세요 저녁 머거요",
            "corrected": "안녕하세요 저녁 먹어요",
            "type": "타이포/띄어쓰기"
        },
        {
            "original": "안녕하세요 저녁 먹어요",
            "corrected": "안녕하세요, 저녁 먹어요.",
            "type": "문법/자연스러움"
        }
    ],
    "stage_texts": {
        "step1": "안녕하세요 저녁 먹어요",
        "final": "안녕하세요, 저녁 먹어요."
    }
}
```

## 🚀 시작하기

### Docker를 이용한 실행 (권장)

1.  **저장소 복제:**

    ```bash
    git clone https://github.com/FixMe2025/FixMe_Backend.git
    cd FixMe_Backend
    ```

2.  **.env 파일 생성:**
    `.env.example` 파일을 복사하여 `.env` 파일을 만듭니다.

    ```bash
    cp .env.example .env
    ```

3.  **Docker 컨테이너 빌드 및 실행:**

    ```bash
    docker-compose up --build
    ```

4.  **API 접속:**

    브라우저나 API 클라이언트에서 `http://localhost:8000`으로 접속하여 서비스를 이용할 수 있습니다. API 문서는 `http://localhost:8000/docs`에서 확인 가능합니다.

### 로컬 환경에서 직접 실행

1.  **가상 환경 생성 및 활성화:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  **의존성 설치:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **.env 파일 생성:**
    `.env.example` 파일을 복사하여 `.env` 파일을 만듭니다.

4.  **애플리케이션 실행:**

    ```bash
    uvicorn app.main:app --reload
    ```

## ⚙️ 설정

애플리케이션의 주요 설정은 `.env` 파일을 통해 관리합니다.

| 변수                    | 설명                                       | 기본값                         |
| ----------------------- | ------------------------------------------ | ------------------------------ |
| `ENVIRONMENT`           | 실행 환경 (development/production)         | `development`                  |
| `LOG_LEVEL`             | 로깅 레벨                                  | `INFO`                         |
| `GENERATIVE_MODEL_NAME` | 사용할 주요 생성형 모델 이름               | `beomi/KoAlpaca-Polyglot-5.8B` |
| `SECONDARY_MODEL_NAME`  | 보조 타이포 교정 모델 이름                 | `j5ng/et5-typos-corrector`     |
| `GRAMMAR_MODEL_NAME`    | LangGraph 파이프라인용 문법 교정 모델      | `theSOL1/kogrammar-base`       |
| `MODEL_CACHE_DIR`       | 모델 캐시 디렉토리                         | `/models` (Docker)             |
| `MAX_TEXT_LENGTH`       | 최대 처리 가능 텍스트 길이 (자)            | `2000`                         |
| `USE_GPU`               | GPU 사용 여부                              | `False`                        |
| `API_HOST`              | API 호스트 주소                            | `0.0.0.0`                      |
| `API_PORT`              | API 포트 번호                              | `8000`                         |

## ⚖️ 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.
