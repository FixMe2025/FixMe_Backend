from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Tuple
import logging
import torch
import re

from app.models.spellcheck import Correction
from app.core.config import get_settings

# 로깅 설정
logger = logging.getLogger(__name__)
settings = get_settings()

class SpellCheckService:
    def __init__(self):
        # 모델과 토크나이저는 초기에는 None으로 두고, 필요할 때 로딩
        self.tokenizer = None
        self.model = None
        self.secondary_tokenizer = None
        self.secondary_model = None

        # GPU 사용 가능하면 CUDA 사용, 아니면 CPU 사용
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"

        # 모델이 로딩되었는지 체크하는 플래그
        self._models_loaded = False

    def _ensure_models_loaded(self):
        """
        모델이 아직 로드되지 않았다면 로딩하는 함수
        - 실제 텍스트 처리 전에 항상 호출 필요
        """
        if not self._models_loaded:
            self._load_models()
            self._models_loaded = True

    def _load_models(self):
        """
        사전 학습된 모델과 토크나이저 로딩
        - Hugging Face에서 지정된 모델명으로 불러옴
        """
        try:
            logger.info(f"모델 로딩 중: {settings.generative_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.generative_model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.generative_model_name,
                cache_dir=settings.model_cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )

            # CPU 환경일 경우 수동으로 모델 디바이스 설정
            if self.device == "cpu":
                self.model = self.model.to(self.device)

            # 보조 모델은 주석 처리 (필요 시 사용)
            logger.info(f"보조 모델 로딩 (선택 사항): {settings.secondary_model_name}")
            # self.secondary_tokenizer = AutoTokenizer.from_pretrained(settings.secondary_model_name)
            # self.secondary_model = AutoModelForSeq2SeqLM.from_pretrained(settings.secondary_model_name)

            logger.info("모델 로딩 완료")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise

    def check_spelling(self, text: str) -> Tuple[str, List[Correction]]:
        """
        입력 문장에 대해 맞춤법 교정 수행
        - 반환값: (교정된 문장, 교정 리스트)
        """
        try:
            self._ensure_models_loaded()  # 모델이 로딩되어 있는지 확인

            corrected_text = self._correct_with_kogrammar(text)
            corrections = self._extract_corrections(text, corrected_text)

            return corrected_text, corrections
        except Exception as e:
            logger.error(f"맞춤법 검사 중 오류: {e}")
            return text, []

    def _correct_with_kogrammar(self, text: str) -> str:
        """
        KoGrammar 모델을 이용한 맞춤법 교정 로직
        """
        try:
            self._ensure_models_loaded()

            # 입력 문장을 교정 프롬프트로 만듦
            prompt = f"맞춤법을 교정해주세요: {text}"

            # 토큰화
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 텍스트 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=min(512, inputs['input_ids'].shape[1] * 2),
                    num_beams=3,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # 디코딩
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # 생성된 텍스트 정리
            corrected = self._clean_generated_text(corrected)

            return corrected if corrected and corrected != text else text
        except Exception as e:
            logger.error(f"KoGrammar 교정 중 오류: {e}")
            return text

    def _clean_generated_text(self, text: str) -> str:
        """
        생성된 문장에서 줄바꿈, 특수토큰 등 불필요한 요소 제거
        """
        text = text.strip()
        text = text.split('\n')[0]  # 첫 줄만 사용
        text = re.sub(r'<[^>]+>', '', text)  # <unk> 같은 토큰 제거
        return text.strip()

    def _extract_corrections(self, original: str, corrected: str) -> List[Correction]:
        """
        원문과 교정문을 비교하여 바뀐 부분을 Correction 리스트로 반환
        """
        corrections = []

        original_words = original.split()
        corrected_words = corrected.split()

        if len(original_words) != len(corrected_words) or original != corrected:
            corrections.append(
                Correction(
                    original=original,
                    corrected=corrected,
                    type="맞춤법 교정"
                )
            )
        else:
            for orig_word, corr_word in zip(original_words, corrected_words):
                if orig_word != corr_word:
                    corrections.append(
                        Correction(
                            original=orig_word,
                            corrected=corr_word,
                            type="맞춤법 교정"
                        )
                    )
        return corrections

    def is_healthy(self) -> bool:
        """
        서비스 상태 확인 (모델 로딩 여부 및 간단한 테스트 수행)
        """
        try:
            self._ensure_models_loaded()
            test_result, _ = self.check_spelling("안녕하세요")
            return test_result is not None
        except Exception:
            return False


# 싱글톤 인스턴스 (FastAPI 등에서 import 하여 공유)
spell_check_service = SpellCheckService()
