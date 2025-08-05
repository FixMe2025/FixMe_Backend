from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Tuple, Optional
import logging
import torch
import re

from app.models.spellcheck import Correction
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TypoCorrectorService:
    """j5ng/et5-typos-corrector 모델을 사용한 보조 맞춤법 교정 서비스"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading typo corrector model: {settings.secondary_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.secondary_model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.secondary_model_name,
                cache_dir=settings.model_cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
                
            logger.info("Typo corrector model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load typo corrector model: {e}")
            self.tokenizer = None
            self.model = None

    def correct_typos(self, text: str) -> Tuple[str, List[Correction]]:
        """타이포 교정을 수행합니다."""
        if not self.model or not self.tokenizer:
            logger.warning("Typo corrector model not loaded, returning original text")
            return text, []
            
        try:
            # 토큰화
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=len(text.split()) + 50,
                    num_beams=3,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 결과 디코딩
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            corrected = self._clean_generated_text(corrected)
            
            # 교정사항 추출
            corrections = self._extract_corrections(text, corrected)
            
            return corrected if corrected != text else text, corrections
            
        except Exception as e:
            logger.error(f"Error in typo correction: {e}")
            return text, []

    def _clean_generated_text(self, text: str) -> str:
        """생성된 텍스트에서 불필요한 부분 제거"""
        text = text.strip()
        # 줄바꿈 제거
        text = text.split('\n')[0]
        # 특수 토큰 제거
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def _extract_corrections(self, original: str, corrected: str) -> List[Correction]:
        """원본과 교정된 텍스트를 비교하여 교정사항 추출"""
        corrections = []
        
        if original != corrected:
            # 간단한 단어 단위 비교로 교정사항 추출
            original_words = original.split()
            corrected_words = corrected.split()
            
            if len(original_words) == len(corrected_words):
                # 단어별 비교
                for orig_word, corr_word in zip(original_words, corrected_words):
                    if orig_word != corr_word:
                        corrections.append(
                            Correction(
                                original=orig_word,
                                corrected=corr_word,
                                type="타이포 교정"
                            )
                        )
            else:
                # 길이가 다른 경우 전체를 하나의 교정으로 처리
                corrections.append(
                    Correction(
                        original=original,
                        corrected=corrected,
                        type="타이포 교정"
                    )
                )
        
        return corrections

    def is_healthy(self) -> bool:
        """서비스 상태 확인"""
        try:
            if self.model is None or self.tokenizer is None:
                return False
            
            # 간단한 테스트
            test_result, _ = self.correct_typos("안녕하세요")
            return test_result is not None
        except Exception:
            return False

# 싱글톤 인스턴스 (선택적으로 사용)
typo_corrector_service = TypoCorrectorService()