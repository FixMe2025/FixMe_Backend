from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict, Optional
import logging
import torch
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TextImprovementService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self._models_loaded = False

    def _ensure_models_loaded(self):
        """모델이 아직 로드되지 않았다면 로딩하는 함수"""
        if not self._models_loaded:
            self._load_model()
            self._models_loaded = True

    def _load_model(self):
        try:
            logger.info(f"Loading model: {settings.generative_model_name}")
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
                
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def improve_text(self, text: str, style: str = "formal") -> Dict:
        try:
            self._ensure_models_loaded()
            # 스타일에 따른 프롬프트 생성
            prompt = self._create_prompt(text, style)
            
            # 토큰화
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 생성 - Seq2Seq 모델에 맞게 수정
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=len(prompt.split()) + 100,
                    num_beams=3,
                    num_return_sequences=2,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 결과 처리
            suggestions = []
            for output in outputs:
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                improved_text = self._extract_improved_text(generated_text, prompt)
                if improved_text and improved_text != text and improved_text.strip():
                    suggestions.append({
                        "text": improved_text,
                        "confidence": 0.85
                    })
            
            # 중복 제거
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                if suggestion["text"] not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion["text"])
            
            return {
                "original_text": text,
                "improved_text": unique_suggestions[0]["text"] if unique_suggestions else text,
                "suggestions": unique_suggestions[:3],
                "style_applied": style
            }
            
        except Exception as e:
            logger.error(f"Error in text improvement: {e}")
            return {
                "original_text": text,
                "improved_text": text,
                "suggestions": [],
                "style_applied": style,
                "error": str(e)
            }

    def _create_prompt(self, text: str, style: str) -> str:
        style_descriptions = {
            "formal": "격식있고 정중한",
            "casual": "자연스럽고 편안한", 
            "academic": "학술적이고 정확한",
            "business": "비즈니스에 적합한 전문적인"
        }
        
        style_desc = style_descriptions.get(style, "자연스러운")
        
        return f"다음 문장을 {style_desc} 한국어로 더 자연스럽고 세련되게 개선해주세요: {text}"

    def _extract_improved_text(self, generated_text: str, prompt: str) -> Optional[str]:
        try:
            # 생성된 텍스트에서 개선된 부분만 추출
            improved = generated_text.strip()
            
            # 프롬프트 부분 제거
            if "개선해주세요:" in improved:
                improved = improved.split("개선해주세요:")[-1].strip()
            
            # 불필요한 부분 제거
            improved = improved.split('\n')[0].strip()
            improved = improved.replace('"', '').replace("'", "").strip()
            
            return improved if improved and len(improved) > 0 else None
        except Exception:
            return None

    def is_healthy(self) -> bool:
        try:
            self._ensure_models_loaded()
            if self.model is None or self.tokenizer is None:
                return False
            
            # 간단한 테스트
            test_result = self.improve_text("안녕하세요.", "formal")
            return "error" not in test_result
        except Exception:
            return False

# 싱글톤 인스턴스 (지연 로딩)
_improvement_service = None

def get_improvement_service() -> TextImprovementService:
    global _improvement_service
    if _improvement_service is None:
        _improvement_service = TextImprovementService()
    return _improvement_service

# 하위 호환성을 위한 별칭
improvement_service = get_improvement_service()