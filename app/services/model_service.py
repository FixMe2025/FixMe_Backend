from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from typing import List, Tuple, Dict, Optional
import logging
import torch
import re

from app.models.spellcheck import Correction
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SpellCheckService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.secondary_tokenizer = None
        self.secondary_model = None
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self._load_models()

    def _load_models(self):
        try:
            logger.info(f"Loading primary model: {settings.generative_model_name}")
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
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)

            # 보조 모델 준비 (나중에 사용)
            logger.info(f"Preparing secondary model: {settings.secondary_model_name}")
            # self.secondary_tokenizer = AutoTokenizer.from_pretrained(settings.secondary_model_name)
            # self.secondary_model = AutoModelForSeq2SeqLM.from_pretrained(settings.secondary_model_name)
                
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

    def check_spelling(self, text: str) -> Tuple[str, List[Correction]]:
        try:
            # theSOL1/kogrammar-base 모델을 사용한 맞춤법 교정
            corrected_text = self._correct_with_kogrammar(text)
            corrections = self._extract_corrections(text, corrected_text)
            
            return corrected_text, corrections

        except Exception as e:
            logger.error(f"Error in spell checking with kogrammar: {e}")
            # 에러 시 원본 텍스트 반환
            return text, []

    def _correct_with_kogrammar(self, text: str) -> str:
        try:
            # 맞춤법 교정을 위한 프롬프트 생성
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
            
            # 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=len(prompt.split()) + 50,
                    num_beams=3,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 결과 디코딩
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 프롬프트 부분 제거하고 교정된 텍스트만 추출
            if "교정해주세요:" in corrected:
                corrected = corrected.split("교정해주세요:")[-1].strip()
            
            # 불필요한 부분 제거
            corrected = self._clean_generated_text(corrected)
            
            return corrected if corrected and corrected != text else text
            
        except Exception as e:
            logger.error(f"Error in kogrammar correction: {e}")
            return text

    def _clean_generated_text(self, text: str) -> str:
        # 생성된 텍스트에서 불필요한 부분 제거
        text = text.strip()
        # 줄바꿈 제거
        text = text.split('\n')[0]
        # 특수 토큰 제거
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def _extract_corrections(self, original: str, corrected: str) -> List[Correction]:
        corrections = []
        
        # 간단한 단어 단위 비교로 교정사항 추출
        original_words = original.split()
        corrected_words = corrected.split()
        
        # 길이가 다른 경우 전체를 하나의 교정으로 처리
        if len(original_words) != len(corrected_words) or original != corrected:
            corrections.append(
                Correction(
                    original=original,
                    corrected=corrected,
                    type="맞춤법 교정"
                )
            )
        else:
            # 단어별 비교
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
        try:
            if self.model is None or self.tokenizer is None:
                return False
            
            # 간단한 테스트
            test_result, _ = self.check_spelling("안녕하세요")
            return test_result is not None
        except Exception:
            return False

# 싱글톤 인스턴스
spell_check_service = SpellCheckService()