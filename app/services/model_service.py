import re
import torch
from typing import List, Tuple, Optional
from transformers import AutoTokenizer, AutoModel
import logging

from app.core.config import settings
from app.models.spellcheck import CorrectionSuggestion

logger = logging.getLogger(__name__)


class KoBERTSpellCheckService:
    def __init__(self):
        self.model_name = settings.model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._initialize_model()

    def _initialize_model(self):
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def detect_spelling_errors(self, text: str) -> List[CorrectionSuggestion]:
        corrections = []
        
        # 기본적인 맞춤법 검사 규칙들
        error_patterns = [
            (r'돼지', '되지'),
            (r'되요', '돼요'),
            (r'됬다', '됐다'),
            (r'되였다', '됐다'),
            (r'가르켜', '가르쳐'),
            (r'틀리다', '다르다'),
            (r'왠지', '웬지'),
            (r'않됀다', '안 된다'),
            (r'되가지고', '돼가지고'),
            (r'어떻해', '어떻게'),
            (r'됬어', '됐어'),
            (r'되네요', '돼네요'),
        ]
        
        text_lower = text.lower()
        
        for pattern, correction in error_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start_pos = match.start()
                end_pos = match.end()
                original = match.group()
                
                # 실제 교정된 형태로 변환
                if original.lower() == pattern.lower():
                    suggested = correction
                else:
                    # 대소문자 패턴 유지
                    suggested = self._preserve_case(original, correction)
                
                corrections.append(CorrectionSuggestion(
                    original=original,
                    suggestion=suggested,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    confidence=0.85
                ))
        
        return corrections

    def _preserve_case(self, original: str, correction: str) -> str:
        if original.isupper():
            return correction.upper()
        elif original.istitle():
            return correction.capitalize()
        return correction

    def apply_corrections(self, text: str, corrections: List[CorrectionSuggestion]) -> str:
        corrected_text = text
        
        # 위치 기준으로 역순 정렬하여 인덱스 변경 문제 방지
        corrections_sorted = sorted(corrections, key=lambda x: x.start_pos, reverse=True)
        
        for correction in corrections_sorted:
            corrected_text = (
                corrected_text[:correction.start_pos] +
                correction.suggestion +
                corrected_text[correction.end_pos:]
            )
        
        return corrected_text

    def check_spelling(self, text: str) -> Tuple[str, List[CorrectionSuggestion]]:
        try:
            # 텍스트 전처리
            processed_text = self.preprocess_text(text)
            
            # 맞춤법 오류 검출
            corrections = self.detect_spelling_errors(processed_text)
            
            # 교정 적용
            corrected_text = self.apply_corrections(processed_text, corrections)
            
            return corrected_text, corrections
            
        except Exception as e:
            logger.error(f"Error in spell checking: {e}")
            raise

    def is_healthy(self) -> bool:
        return self.model is not None and self.tokenizer is not None


# 싱글톤 인스턴스
spell_check_service = KoBERTSpellCheckService()