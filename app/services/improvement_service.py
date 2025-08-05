from transformers import AutoTokenizer, AutoModelForCausalLM
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
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading model: {settings.generative_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.generative_model_name,
                cache_dir=settings.model_cache_dir
            )
            self.model = AutoModelForCausalLM.from_pretrained(
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
            # 스타일에 따른 프롬프트 생성
            prompt = self._create_prompt(text, style)
            
            # 토큰화
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    num_return_sequences=2,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 결과 처리
            suggestions = []
            for output in outputs:
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                improved_text = self._extract_improved_text(generated_text, prompt)
                if improved_text and improved_text != text:
                    suggestions.append({
                        "text": improved_text,
                        "confidence": 0.85  # 임시 confidence score
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
                "suggestions": unique_suggestions[:3],  # 최대 3개
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
        
        return f"""다음 문장을 {style_desc} 한국어로 더 자연스럽고 세련되게 개선해주세요.

원문: {text}

개선된 문장:"""

    def _extract_improved_text(self, generated_text: str, prompt: str) -> Optional[str]:
        # 프롬프트 이후의 텍스트만 추출
        try:
            if "개선된 문장:" in generated_text:
                improved = generated_text.split("개선된 문장:")[-1].strip()
                # 불필요한 부분 제거 (줄바꿈, 특수문자 등)
                improved = improved.split('\n')[0].strip()
                return improved if improved else None
            return None
        except Exception:
            return None

    def is_healthy(self) -> bool:
        try:
            if self.model is None or self.tokenizer is None:
                return False
            
            # 간단한 테스트
            test_result = self.improve_text("안녕하세요.", "formal")
            return "error" not in test_result
        except Exception:
            return False

# 싱글톤 인스턴스
improvement_service = TextImprovementService()