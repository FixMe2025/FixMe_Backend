# FixMe - 한글 맞춤법 교정 API

FixMe는 FastAPI를 기반으로 구축된 한글 맞춤법 교정 API 서비스입니다. beomi/KoAlpaca-Polyglot-5.8B 모델을 활용하여 정확하고 빠른 맞춤법 검사 및 교정 기능을 제공하며, j5ng/et5-typos-corrector 모델을 이용한 보조 타이포 교정도 지원합니다.

## 주요 기능

- **맞춤법 검사 및 교정:** 입력된 한글 텍스트의 맞춤법 오류를 찾아내고, 교정된 텍스트와 상세한 교정 내용을 제공합니다.
- **문장 개선 추천:** 생성형 모델을 이용하여 문체에 맞는 자연스러운 문장 개선을 제안합니다.
- **보조 타이포 교정:** j5ng/et5-typos-corrector 모델을 활용해 추가적인 타이포 교정을 수행합니다.
- **상세한 교정 정보:** 각 오류에 대해 원래 단어, 교정된 단어, 그리고 오류 유형을 함께 반환하여 사용자가 오류를 명확하게 이해할 수 있도록 돕습니다.
- **유연한 텍스트 처리:** 최대 1000자까지의 텍스트를 처리할 수 있어, 짧은 문장부터 긴 글까지 다양한 요구사항에 대응할 수 있습니다.
- **상태 확인 및 서비스 정보:** API의 현재 상태를 확인할 수 있는 헬스 체크(Health Check) 엔드포인트와 서비스의 주요 정보를 제공하는 엔드포인트를 지원합니다.

## 기술 스택

- **언어:** Python 3.11
- **프레임워크:** FastAPI
- **AI 모델:** beomi/KoAlpaca-Polyglot-5.8B (주요), j5ng/et5-typos-corrector (보조)
- **컨테이너:** Docker

## API 엔드포인트

| Method | Endpoint                             | 설명                            |
| ------ | ------------------------------------- | ------------------------------- |
| POST   | `/api/v1/spellcheck/check`            | 맞춤법 검사를 수행합니다.       |
| POST   | `/api/v1/improve/text`                | 문장 개선을 수행합니다.         |
| POST   | `/api/v1/comprehensive/comprehensive` | 종합 맞춤법/개선 검사를 수행합니다. |
| GET    | `/api/v1/spellcheck/health`           | 맞춤법 서비스 상태를 확인합니다. |
| GET    | `/api/v1/improve/health`              | 문장 개선 서비스 상태를 확인합니다. |
| GET    | `/api/v1/comprehensive/health`        | 종합 서비스 상태를 확인합니다. |
| GET    | `/api/v1/spellcheck/info`             | 맞춤법 서비스 정보를 제공합니다. |
| GET    | `/api/v1/improve/info`                | 문장 개선 서비스 정보를 제공합니다. |
| GET    | `/api/v1/comprehensive/info`          | 종합 서비스 정보를 제공합니다. |

### 맞춤법 검사 (`/api/v1/spellcheck/check`)

- **Request Body:**

```json
{
  "text": "사용자가 입력한 텍스트입니다."
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
  "has_errors": true,
  "total_corrections": 1,
  "message": "맞춤법 검사가 완료되었습니다."
}
```

## 시작하기

### Docker를 이용한 실행

1.  **저장소 복제:**

    ```bash
    git clone https://github.com/your-username/FixMe_Backend.git
    cd FixMe_Backend
    ```

2.  **Docker 컨테이너 빌드 및 실행:**

    ```bash
    docker-compose up --build
    ```

3.  **API 접속:**

    이제 브라우저나 API 클라이언트에서 `http://localhost:8000`으로 접속하여 서비스를 이용할 수 있습니다. API 문서는 `http://localhost:8000/docs`에서 확인 가능합니다.

### 로컬 환경에서 직접 실행

1.  **저장소 복제 및 이동:**

    ```bash
    git clone https://github.com/your-username/FixMe_Backend.git
    cd FixMe_Backend
    ```

2.  **가상 환경 생성 및 활성화:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **의존성 설치:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **애플리케이션 실행:**

    ```bash
    uvicorn app.main:app --reload
    ```

## 설정

애플리케이션의 주요 설정은 `.env` 파일을 통해 관리할 수 있습니다. `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 필요에 따라 설정을 변경하세요.

| 변수              | 설명                               | 기본값                  |
| ----------------- | ---------------------------------- | ----------------------- |
| `ENVIRONMENT`           | 실행 환경 (development/production) | `development`           |
| `LOG_LEVEL`             | 로깅 레벨                          | `INFO`                  |
| `GENERATIVE_MODEL_NAME` | 사용할 주요 생성형 모델 이름      | `beomi/KoAlpaca-Polyglot-5.8B` |
| `SECONDARY_MODEL_NAME`  | 보조 타이포 교정 모델 이름        | `j5ng/et5-typos-corrector` |
| `MODEL_CACHE_DIR`       | 모델 캐시 디렉토리                 | `./models`              |
| `MAX_TEXT_LENGTH`       | 최대 처리 가능 텍스트 길이         | `1000`                  |
| `USE_GPU`               | GPU 사용 여부                      | `False`                 |

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.